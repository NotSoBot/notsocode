import enum
import io
import os
import subprocess
import tarfile
import threading
import time

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Iterator, Optional, Union

import docker
import docker.errors
import requests

from notsocode.utilities.constants import BaseImages, Languages, LanguagePrepends
from notsocode.utilities.wrappers import asyncify



DEFAULT_TIMEOUT = 15


class ExecutionTimeout(Exception):
    def __init__(self, timeout: float):
        self.timeout = timeout
        super().__init__(f'Code Execution took longer than {timeout:g} seconds')


class ImageBuilding(Exception):
    # another call is building the image and it didn't finish within BUILD_WAIT, the server answers this with a 503
    def __init__(self, tag: str):
        self.tag = tag
        super().__init__(f'{tag} is being built, try again in a minute')


USER = os.getenv('NOTSOCODE_USER', 'notsocoder')
USER_UID = os.getenv('NOTSOCODE_USER_UID', '42069')

DIRECTORY_INPUT = '/input'
DIRECTORY_OUTPUT = '/output'

DIRECTORY_HOME = f'/home/{USER}'
DIRECTORY_HOME_INPUT = DIRECTORY_HOME + DIRECTORY_INPUT
DIRECTORY_HOME_OUTPUT = DIRECTORY_HOME + DIRECTORY_OUTPUT
FILENAME_SCRIPT = os.getenv('NOTSOCODE_SCRIPT_FILE', 'script')
FILENAME_STDIN = os.getenv('NOTSOCODE_STDIN_FILE', 'stdin')

MAX_CONNECTION_BURST  = int(os.getenv('NOTSOCODE_PROCESS_MAX_CONNECTION_BURST', 5))
MAX_CONNECTION_RATE  = os.getenv('NOTSOCODE_PROCESS_MAX_CONNECTION_RATE', '3/sec')
MAX_CONNECTION_SPEED = os.getenv('NOTSOCODE_PROCESS_MAX_CONNECTION_SPEED', '160mbit')

MAX_CPUS = float(os.getenv('NOTSOCODE_PROCESS_MAX_CPUS', 4))
# relative weight when the host is out of cpu, docker's default is 1024; below it dockerd and the server win then,
# so container setup/removal doesn't eat into the jobs' timeouts. MAX_CPUS still caps a job when the host is idle
CPU_SHARES = int(os.getenv('NOTSOCODE_PROCESS_CPU_SHARES', 512))
MAX_FILES = int(os.getenv('NOTSOCODE_PROCESS_MAX_FILES', 10))
MAX_MEMORY = os.getenv('NOTSOCODE_PROCESS_MAX_MEMORY', '2048m')
MAX_RESULT_LENGTH = 1 * 1024 * 1024
# writable layer quota per container, e.g. '512m'; off by default since docker needs overlay2 on xfs with pquota
MAX_STORAGE_SIZE = os.getenv('NOTSOCODE_PROCESS_MAX_STORAGE', '')
MAX_TIMEOUT = float(os.getenv('NOTSOCODE_PROCESS_MAX_TIMEOUT', 45))

ULIMIT_FILE_SIZE = int(os.getenv('NOTSOCODE_PROCESS_ULIMIT_FILE_SIZE', 100 * 1024 * 1024))
ULIMIT_FILES = int(os.getenv('NOTSOCODE_PROCESS_ULIMIT_FILES', 2048))
ULIMIT_MEMORY = 2 * 1024 * 1024 * 1024
# enforced per container with pids_limit, an nproc ulimit is counted per host uid so every job would share it
ULIMIT_PROCESSES = int(os.getenv('NOTSOCODE_PROCESS_ULIMIT_PROCESSES', 512))


# private / special-use ranges a sandboxed job should never reach
BLOCKED_DESTS = [
    '10.0.0.0/8',
    '172.16.0.0/12',
    '192.168.0.0/16',
    '169.254.0.0/16',   # link-local — includes 169.254.169.254 cloud metadata
    '100.64.0.0/10',    # carrier-grade NAT / some cloud internal
]

# outbound tcp ports a job can't connect to anywhere, 25 is direct-to-mx spam that gets the host's ip listed
BLOCKED_PORTS = [25]

# the container's root only runs the entrypoint (chown/chmod the job files, su to the user, prune /output),
# everything else docker gives by default (NET_RAW, MKNOD, SETFCAP, ...) is dropped
CAPABILITIES = [
    'CHOWN',
    'DAC_OVERRIDE',     # pruning /output dirs the user made unreadable
    'FOWNER',           # chmod on files the user owns
    'SETGID',
    'SETUID',
]


# every rule a job adds carries this comment, so the orphan sweep can tell ours apart from anything else
RULE_TAG = 'notsocode-job'
RULE_CHAINS = ('DOCKER-USER', 'INPUT')

# job networks and containers carry this label so pruning never touches anything that isn't ours
JOB_LABEL = 'notsocode.job'
NETWORK_LABEL = JOB_LABEL
# networks are pruned and orphaned rules swept at most this often, every job triggers it
NETWORK_MAINTENANCE_INTERVAL = int(os.getenv('NOTSOCODE_NETWORK_MAINTENANCE_INTERVAL', 60))
# a job container this old is one nobody removed (its request was dropped, removing it failed, or the server stopped
# mid-run). A live one is created after the image build and lives for its run, reading its output and its removal, so
# two minutes on top of the max timeout is plenty. Not 0 at startup either, in case another process shares the host
STALE_CONTAINER_AGE = int(os.getenv('NOTSOCODE_STALE_CONTAINER_AGE', MAX_TIMEOUT + 120))

# how long a call waits on another call's build of the same image before it gives up with ImageBuilding. Covers the
# cached rebuilds right after a restart (a second or two), a real build takes minutes and isn't worth holding a slot for
BUILD_WAIT = float(os.getenv('NOTSOCODE_BUILD_WAIT', 5))


class _SharedLock:
    '''
    Readers-writer lock: job network setup and teardown share it, the orphan rule sweep takes it exclusively. Without it
    a job could free its subnet and the next job reuse it between the sweep listing the networks and deleting the rules,
    and the sweep would then delete the new job's firewall rules (same specs). Writer first, so a busy server can't
    starve the sweep. Not reentrant: never take `shared` while already holding it
    '''
    def __init__(self):
        self._condition = threading.Condition()
        self._shared = 0
        self._exclusive = False

    @contextmanager
    def shared(self) -> Iterator[None]:
        with self._condition:
            while self._exclusive:
                self._condition.wait()
            self._shared += 1
        try:
            yield
        finally:
            with self._condition:
                self._shared -= 1
                if not self._shared:
                    self._condition.notify_all()

    @contextmanager
    def exclusive(self) -> Iterator[None]:
        with self._condition:
            while self._exclusive:
                self._condition.wait()
            # set before waiting out the holders, so new `shared` callers queue behind it
            self._exclusive = True
            while self._shared:
                self._condition.wait()
        try:
            yield
        finally:
            with self._condition:
                self._exclusive = False
                self._condition.notify_all()


firewall_lock = _SharedLock()


def _ipt(args, check=True):
    # -w waits for the xtables lock instead of failing when dockerd or another job's thread holds it
    return subprocess.run(['iptables', '-w', *args], check=check, capture_output=True, text=True)


def _tagged(spec):
    # comment match goes right before the `-j target`, same place `iptables -S` prints it
    return [*spec[:-2], '-m', 'comment', '--comment', RULE_TAG, *spec[-2:]]


def _ipt_add(chain, spec):
    _ipt(['-I', chain, *_tagged(spec)])


def _ipt_del(spec, chain='DOCKER-USER'):
    _ipt(['-D', chain, *_tagged(spec)], check=False)


def _tc(args, check=True):
    return subprocess.run(['tc', *args], check=check, capture_output=True, text=True)


def add_egress_block_rules(subnet: str):
    # Broad DROPs first, then a RETURN for the job's OWN subnet inserted last so it
    # sits ABOVE the drops — otherwise -d 10.0.0.0/8 would also block the container
    # from reaching its own gateway and embedded DNS (job subnet is inside 10/8).
    for port in BLOCKED_PORTS:
        _ipt_add('DOCKER-USER', ['-s', subnet, '-p', 'tcp', '--dport', str(port), '-j', 'DROP'])
    for dest in BLOCKED_DESTS:
        _ipt_add('DOCKER-USER', ['-s', subnet, '-d', dest, '-j', 'DROP'])
    _ipt_add('DOCKER-USER', ['-s', subnet, '-d', subnet, '-j', 'RETURN'])


def del_egress_block_rules(subnet: str):
    _ipt_del(['-s', subnet, '-d', subnet, '-j', 'RETURN'])
    for dest in BLOCKED_DESTS:
        _ipt_del(['-s', subnet, '-d', dest, '-j', 'DROP'])
    for port in BLOCKED_PORTS:
        _ipt_del(['-s', subnet, '-p', 'tcp', '--dport', str(port), '-j', 'DROP'])


def add_host_block_rule(subnet: str):
    # DOCKER-USER only sees forwarded traffic, anything addressed to the host itself (bridge gateway,
    # public ip, services bound to 0.0.0.0) goes through INPUT instead
    _ipt_add('INPUT', ['-s', subnet, '-j', 'DROP'])


def del_host_block_rule(subnet: str):
    _ipt_del(['-s', subnet, '-j', 'DROP'], chain='INPUT')


def add_conn_limit_rule(subnet: str):
    # Meter NEW outbound connections to CONN_RATE. "under-rate -> RETURN" above
    # "NEW -> DROP". -I inserts at top, so insert DROP first, RETURN second.
    # Only NEW is metered; established/return traffic is untouched.
    _ipt_add('DOCKER-USER', [
        '-s', subnet, '-m', 'conntrack', '--ctstate', 'NEW',
        '-j', 'DROP',
    ])
    _ipt_add('DOCKER-USER', [
        '-s', subnet, '-m', 'conntrack', '--ctstate', 'NEW',
        '-m', 'limit', '--limit', str(MAX_CONNECTION_RATE), '--limit-burst', str(MAX_CONNECTION_BURST),
        '-j', 'RETURN',
    ])


def del_conn_limit_rule(subnet: str):
    _ipt_del([
      '-s', subnet, '-m', 'conntrack', '--ctstate', 'NEW',
      '-m', 'limit', '--limit', str(MAX_CONNECTION_RATE), '--limit-burst', str(MAX_CONNECTION_BURST),
      '-j', 'RETURN',
    ])
    _ipt_del(['-s', subnet, '-m', 'conntrack', '--ctstate', 'NEW', '-j', 'DROP'])


class _ChunkReader(io.RawIOBase):
    # file-like view of docker's chunk generator so tarfile can stream it
    def __init__(self, chunks):
        self._chunks = iter(chunks)
        self._buffer = b''

    def readable(self):
        return True

    def readinto(self, buffer):
        while not self._buffer:
            try:
                self._buffer = next(self._chunks)
            except StopIteration:
                return 0
        size = min(len(buffer), len(self._buffer))
        buffer[:size] = self._buffer[:size]
        self._buffer = self._buffer[size:]
        return size


def _bridge_name(network_id: str):
    return 'br-' + network_id[:12]


def add_bandwidth_limit(network_id: str):
    _tc([
        'qdisc', 'add', 'dev', _bridge_name(network_id), 'root', 'tbf',
        'rate', str(MAX_CONNECTION_SPEED), 'burst', '32kbit', 'latency', '50ms',
    ])


def del_bandwidth_limit(network_id: str):
    _tc(['qdisc', 'del', 'dev', _bridge_name(network_id), 'root'], check=False)



class BuildState(enum.Enum):
    BUILDING = 'building'
    BUILT = 'built'
    FAILED = 'failed'


class ImageBuild:
    '''
    One docker build of a tag in this process, shared by every call that needs the tag while it runs.
    BUILDING -> BUILT (kept, later calls skip the build) | FAILED (dropped from `NotSoCode.builds`, the next call retries)
    A tag missing from `NotSoCode.builds` isn't built in this process yet, the first call builds it (cached by docker)
    '''
    def __init__(self, tag: str):
        self.tag = tag
        self.state = BuildState.BUILDING
        self.error: Optional[BaseException] = None
        self._done = threading.Event()

    def finish(self, error: Optional[BaseException] = None):
        if self.state is not BuildState.BUILDING:
            raise RuntimeError(f'{self.tag} build already {self.state.value}')
        self.error = error
        self.state = BuildState.FAILED if error is not None else BuildState.BUILT
        self._done.set()

    def wait(self, timeout: float) -> bool:
        return self._done.wait(timeout)



class NotSoCode:
    builds: dict[str, ImageBuild] = {}
    # builds run on executor threads, the claim of a tag has to be atomic
    build_lock = threading.Lock()
    client_lock = threading.Lock()
    network_maintenance_lock = threading.Lock()
    network_maintenance_last = 0.0

    client = None
    client_api = None
    dockerfiles_directory = '/dockerfiles'
    tag_prepend = os.getenv('NOTSOCODE_DOCKER_TAG_PREPEND', 'notsocode')

    @classmethod
    def ensure_docker_user_ready(cls):
        if _ipt(['-S', 'DOCKER-USER'], check=False).returncode != 0:
            raise RuntimeError('DOCKER-USER chain missing — cannot enforce network policy')

    @classmethod
    def sweep_orphan_rules(cls, client, pool_cidr='10.200.0.0/16'):
        # Remove rules left behind by jobs whose network is gone (crashed process, pruned network).
        # Tagged rules are ours wherever their subnet is; untagged DOCKER-USER rules predate tagging
        # and are only touched inside pool_cidr, the old guard.
        import ipaddress
        pool = ipaddress.ip_network(pool_cidr)

        # no job sets up or tears down its network meanwhile, so the rules and the networks are one consistent snapshot
        # and a subnet freed and reused mid-sweep can't lose the new job's rules
        with firewall_lock.exclusive():
            cls._sweep_orphan_rules(client, pool)

    @classmethod
    def _sweep_orphan_rules(cls, client, pool):
        import ipaddress

        rules = {chain: _ipt(['-S', chain], check=False).stdout.splitlines() for chain in RULE_CHAINS}

        live = set()
        for net in client.networks.list():
            for cfg in (net.attrs.get('IPAM', {}).get('Config') or []):
                if cfg.get('Subnet'):
                    live.add(cfg['Subnet'])

        for chain, lines in rules.items():
            for line in lines:
                # some iptables versions quote the comment, the rule spec itself has no quoted values
                parts = [x.strip('"') for x in line.split()]
                if not parts or parts[0] != '-A' or '-s' not in parts:
                    continue
                subnet = parts[parts.index('-s') + 1]
                if subnet in live:
                    continue

                tagged = '--comment' in parts and parts[parts.index('--comment') + 1] == RULE_TAG
                if not tagged:
                    # INPUT holds the host's own rules, we only ever remove tagged ones there
                    if chain == 'INPUT':
                        continue
                    try:
                        if not ipaddress.ip_network(subnet, strict=False).subnet_of(pool):
                            continue
                    except ValueError:
                        continue
                _ipt(['-D', chain, *parts[2:]], check=False)

    @classmethod
    def maintain_networks(cls, client):
        # prune our stale job networks then sweep the rules they left, throttled since every job calls this
        with cls.network_maintenance_lock:
            now = time.time()
            if now - cls.network_maintenance_last < NETWORK_MAINTENANCE_INTERVAL:
                return
            cls.network_maintenance_last = now

        # first, so the networks of the containers it removes are pruned in this same pass
        try:
            cls.remove_stale_containers(client)
        except Exception as error:
            print('error removing stale containers', str(error), flush=True)

        try:
            until =(datetime.now(timezone.utc) - timedelta(minutes=3)).strftime('%Y-%m-%dT%H:%M:%SZ')
            result = client.networks.prune(filters={'label': NETWORK_LABEL, 'until': until})
            print(f"Pruned {len(result['NetworksDeleted'] or [])} networks", flush=True)
        except Exception as error:
            print('error pruning networks', str(error), flush=True)

        try:
            cls.sweep_orphan_rules(client)
        except Exception as error:
            print('error sweeping firewall rules', str(error), flush=True)

    @classmethod
    def remove_stale_containers(cls, client, max_age: float = STALE_CONTAINER_AGE):
        # job containers nobody removed: a dropped request, a remove that failed (still running, its rules kept it boxed
        # in until now), or a server that stopped mid-run. Only labelled ones, older containers predate the label
        removed = 0
        cutoff = time.time() - max_age
        for container in client.containers.list(all=True, sparse=True, filters={'label': JOB_LABEL}):
            if cutoff < (container.attrs.get('Created') or 0):
                continue
            try:
                container.remove(force=True)
                removed += 1
            except docker.errors.NotFound:
                pass
            except Exception as error:
                print('error removing stale container', container.id, str(error), flush=True)
        if removed:
            print(f'Removed {removed} stale containers', flush=True)

    @classmethod
    def generate_tag(cls, language_: Languages, version: Optional[str] = None):
        language = language_.language
        version = version or language_.default_version
        return f'{cls.tag_prepend}-{language}:{version}'

    @classmethod
    def get_api_client(cls):
        with cls.client_lock:
            if not cls.client_api:
                cls.client_api = docker.APIClient(base_url=os.getenv('DOCKER_BASE_URL'))
            return cls.client_api

    @classmethod
    def get_client(cls):
        # the client is only kept once the network policy checks pass, so a failed check fails every call instead of
        # only the first one. The server calls this at startup, so it refuses to start then
        with cls.client_lock:
            if not cls.client:
                if os.getenv('DOCKER_BASE_URL'):
                    client = docker.DockerClient(base_url=os.getenv('DOCKER_BASE_URL'))
                else:
                    client = docker.from_env()
                cls.ensure_docker_user_ready()
                cls.sweep_orphan_rules(client)
                cls.client = client
            return cls.client

    @classmethod
    @asyncify()
    def get_example_code(cls, language_: Languages, version: Optional[str] = None) -> str:
        return cls.get_example_code_sync(language_, version=version)

    @classmethod
    def get_example_code_sync(cls, language_: Languages, version: Optional[str] = None) -> str:
        extension = language_.extension
        language = language_.language
        extension = language_.extension
        version = version or language_.default_version

        directory = os.path.dirname(__file__) + os.path.join(cls.dockerfiles_directory, language, version or '')
        filepath = os.path.join(directory, f'test.{extension}')
        if not os.path.exists(filepath):
            for filename in os.listdir(directory):
                if filename.startswith('test.') and filename.endswith(f'.{extension}'):
                    filepath = os.path.join(directory, filename)
                    break

        if not os.path.exists(filepath):
            raise Exception(f'Test for {cls.generate_tag(language_, version=version)} does not exist.')

        with open(filepath, 'r') as f:
            code = f.read()

        return code

    @classmethod
    @asyncify()
    def build(cls, language_: Languages, version: Optional[str] = None, **kwargs):
        return cls.build_sync(language_, version=version, **kwargs)

    @classmethod
    def build_sync(cls, language_: Languages, version: Optional[str] = None, base: Optional[BaseImages] = None, **kwargs):
        print(kwargs, flush=True)
        language = language_.language
        version = version or language_.default_version
    
        directory = os.path.dirname(__file__) + os.path.join(cls.dockerfiles_directory, language, version or '')
        if not os.path.exists(directory):
            raise Exception('Invalid Build')

        # one BUILD_WAIT for the whole chain (builder, base, language), not one per image
        wait_deadline = time.time() + BUILD_WAIT
        if base is not None:
            cls.build_base_sync(base, wait_deadline=wait_deadline)

        tag = cls.generate_tag(language_, version=version)
        return cls._build_sync(directory, tag, base=base, wait_deadline=wait_deadline, **kwargs)

    @classmethod
    def build_base_sync(cls, base: BaseImages, wait_deadline: Optional[float] = None, **kwargs):
        if base != BaseImages.BUILDER:
            cls.build_base_sync(BaseImages.BUILDER, wait_deadline=wait_deadline)
        directory = os.path.dirname(__file__) + os.path.join(cls.dockerfiles_directory, base.value[0], base.value[1])
        return cls._build_sync(directory, tag=base.tag, wait_deadline=wait_deadline)

    @classmethod
    def forget_build(cls, tag: str):
        # BUILT -> missing, for an image that was removed outside this process (`docker image prune -a`), so the next
        # call builds it again instead of every one failing until a restart
        with cls.build_lock:
            build = cls.builds.get(tag)
            if build is not None and build.state is BuildState.BUILT:
                del cls.builds[tag]

    @classmethod
    def _build_sync(
        cls,
        directory: str,
        tag: str,
        base: Optional[BaseImages] = None,
        wait_deadline: Optional[float] = None,
        **kwargs,
    ):
        with cls.build_lock:
            build = cls.builds.get(tag)
            owner = build is None
            if build is None:
                build = cls.builds[tag] = ImageBuild(tag)

        if not owner:
            # another call is building it (a shared base image, mostly): wait for that build instead of failing, a
            # cached rebuild after a restart is done in a second or two
            wait = BUILD_WAIT if wait_deadline is None else max(0.0, wait_deadline - time.time())
            if not build.wait(wait):
                raise ImageBuilding(tag)
            if build.state is BuildState.FAILED:
                raise Exception(f'{tag} failed to build: {build.error}') from build.error
            return None

        kwargs['buildargs'] = {
            'BASE_IMAGE': base.tag if base else BaseImages.BOOKWORM_SLIM.tag,
            'DIRECTORY_HOME': DIRECTORY_HOME,
            'DIRECTORY_OUTPUT': DIRECTORY_HOME_OUTPUT,
            'FILENAME_SCRIPT': FILENAME_SCRIPT,
            'FILENAME_STDIN': FILENAME_STDIN,
            'MAX_FILES': str(MAX_FILES),
            'USER': USER,
            'USER_UID': USER_UID,
        }
 
        print(f'Building {tag}.', flush=True)
        try:
            client = cls.get_api_client()
            lines = list(client.build(path=directory, tag=tag, forcerm=True, decode=True, **kwargs))
            print(lines, flush=True)

            if not lines or 'errorDetail' in lines[-1]:
                raise Exception('\n'.join(x.get('error', x.get('stream', '')) for x in lines) or f'{tag} failed to build')
        except BaseException as error:
            # dropped first, so the next call retries the build instead of seeing this failed one
            with cls.build_lock:
                cls.builds.pop(tag, None)
            build.finish(error)
            raise

        build.finish()
        return lines

    @classmethod
    def create_tar(cls, files: list[tuple[bytes, str]], directories: list[str] = []):
        tar_stream = io.BytesIO()
        tar = tarfile.open(fileobj=tar_stream, mode='w')

        for directory in directories:
            info = tarfile.TarInfo(directory)
            info.type = tarfile.DIRTYPE
            tar.addfile(info)

        for buffer, filename in files:
            info = tarfile.TarInfo(name=filename)
            info.size = len(buffer)
            info.mtime = int(time.time())
            tar.addfile(info, fileobj=io.BytesIO(buffer))

        tar.close()
        tar_stream.seek(0)
        return tar_stream

    @classmethod
    @asyncify()
    def build_and_test(cls, language_: Languages, version: Optional[str] = None) -> bool:
        code = cls.get_example_code_sync(language_, version=version)
        job = cls.create_job_sync(language_, code, version=version)
        result = job.execute_sync()
        return result['result']['output'] == 'Hello, World!'

    @classmethod
    @asyncify()
    def create_job(cls, *args, **kwargs):
        return cls.create_job_sync(*args, **kwargs)

    @classmethod
    def create_job_sync(
        cls,
        language: Languages,
        code: str,
        version: Optional[str] = None,
        files: list[dict] = [],
        max_memory: Union[int, str] = MAX_MEMORY,
        stdin: str = '',
        allow_network: bool = True,
        *args,
        **kwargs,
    ):
        if language in LanguagePrepends:
            code = LanguagePrepends[language] + code

        now = time.time()
        tar_stream = cls.create_tar(
            files=[
                (code.encode(), f'{FILENAME_SCRIPT}.{language.extension}'),
                (stdin.encode(), FILENAME_STDIN),
                *[(x['buffer'], DIRECTORY_INPUT + '/' + x['filename']) for x in files],
            ],
            directories=[DIRECTORY_INPUT, DIRECTORY_OUTPUT],
        )

        cls.build_sync(language, version=version, base=BaseImages.BOOKWORM_SLIM)
        tag = cls.generate_tag(language, version=version)

        client = cls.get_client()
        # every job, so stale containers are found even when only network-less jobs come in
        cls.maintain_networks(client)

        job = Job(None, language, version=version or language.default_version)

        network = None
        if allow_network:
            setup_error: Optional[Exception] = None
            # the network and its rules appear together as far as the orphan rule sweep can see
            with firewall_lock.shared():
                try:
                    network = client.networks.create(f'{time.time()}', labels={JOB_LABEL: '1'})
                except Exception as error:
                    # runs without a network then, which fails closed
                    print('error creating network', str(error), flush=True)

                if network:
                    job.network = network
                    try:
                        network.reload()
                        subnet = network.attrs['IPAM']['Config'][0]['Subnet']
                        job.network_subnet = subnet

                        # order: conn-limit first (ends up at bottom), egress-block last
                        # (ends up on top) so internal DROPs sit above the rate-limit RETURN.
                        add_conn_limit_rule(subnet)
                        add_egress_block_rules(subnet)
                        add_host_block_rule(subnet)
                        add_bandwidth_limit(network.id)
                    except Exception as error:
                        setup_error = error

            if setup_error is not None:
                # don't leave the network or a partial rule set behind; outside the lock, kill takes it itself
                job.kill_sync()
                raise setup_error

        container_kwargs: dict = {}
        if network:
            container_kwargs['network'] = network.name
        else:
            container_kwargs['network_disabled'] = True
            container_kwargs['network_mode'] = 'none'
        if MAX_STORAGE_SIZE:
            container_kwargs['storage_opt'] = {'size': MAX_STORAGE_SIZE}

        try:
            environment: dict = {}
            for i in range(len(files)):
                environment[f'FILE_{i + 1}'] = DIRECTORY_HOME_INPUT + '/' + files[i]['filename']

            container = client.containers.create(
                tag,
                cap_add=CAPABILITIES,
                cap_drop=['ALL'],
                cpu_shares=CPU_SHARES,
                detach=True,
                # device read/write limits
                #kernel_memory=1,
                environment=environment,
                labels={
                    # found by `remove_stale_containers` if this job is never killed
                    JOB_LABEL: '1',
                    #'com.docker-tc.enabled': '1',
                    #'com.docker-tc.limit': '20mbps',
                    #'com.docker-tc.delay': '50ms',
                },
                log_config=docker.types.LogConfig(
                    type=docker.types.LogConfig.types.JSON,
                    config={'max-size': f'{MAX_RESULT_LENGTH * 2}b'},
                ),
                mem_limit=max_memory,
                # same as mem_limit so there's no swap on top of it, docker's default doubles it with swap
                memswap_limit=max_memory,
                nano_cpus=int(MAX_CPUS * 1e9),
                pids_limit=ULIMIT_PROCESSES,
                # a setuid binary (su, passwd, ...) can't take the user back to root, su from root down still works
                security_opt=['no-new-privileges'],
                #mounts=[
                #    docker.types.Mount(
                #        target='/home',
                #        source=directory,
                #        type='bind',
                #        #driver_config=docker.types.DriverConfig('local', options={'size': MAX_STORAGE_SIZE}),
                #    ),
                #],

                #network_disabled=True,
                #network_mode='none',

                #user=os.getenv('NOTSOCODE_USER'),
                #tmpfs={
                #    f'{DIRECTORY_HOME}{DIRECTORY_OUTPUT}': 'size=100m',
                #},
                #stdin_open=bool(stdin),
                #tty=bool(stdin),
                ulimits=[
                    #docker.types.Ulimit(name='as', soft=ULIMIT_MEMORY, hard=ULIMIT_MEMORY),
                    docker.types.Ulimit(name='fsize', soft=ULIMIT_FILE_SIZE, hard=ULIMIT_FILE_SIZE),
                    docker.types.Ulimit(name='nofile', soft=ULIMIT_FILES, hard=ULIMIT_FILES),
                ],
                **container_kwargs,
            )
            job.container = container

            tar_stream.seek(0)
            container.put_archive(DIRECTORY_HOME, tar_stream)
        except Exception as error:
            print('error creating container', str(error), flush=True)
            if isinstance(error, docker.errors.ImageNotFound):
                # `docker image prune -a` takes the unused base images too, the language's rebuild needs them back
                for forgotten in (tag, BaseImages.BOOKWORM_SLIM.tag, BaseImages.BUILDER.tag):
                    cls.forget_build(forgotten)
            job.kill_sync()
            raise

        print('done creation', job.language, job.version, int((time.time() - now) * 1000), flush=True)
        return job

    @classmethod
    @asyncify()
    def execute(cls, *args, **kwargs):
        return cls.execute_sync(*args, **kwargs)

    @classmethod
    def execute_sync(cls, *args, timeout: float = DEFAULT_TIMEOUT, **kwargs):
        job = cls.create_job_sync(*args, **kwargs)
        return job.execute_sync(timeout=timeout)


class JobState(enum.Enum):
    CREATED = 'created'    # container (and network) made, the code hasn't started
    RUNNING = 'running'
    FINISHED = 'finished'  # ran or timed out, its container is still there until the job is killed
    KILLED = 'killed'      # container and network removed, final


class Job:
    '''
    CREATED -> RUNNING -> FINISHED -> KILLED, and any state -> KILLED. A job runs once: a second `execute` raises
    instead of starting the exited container again. A kill whose container removal fails leaves the state (and the
    container's firewall rules) as they are, the stale container sweep finishes it later
    '''
    def __init__(
        cls,
        container: Any,
        language: Languages,
        version: str,
        network: Any = None,
        network_subnet: Optional[str] = None,
    ):
        cls.container = container
        cls.language = language
        cls.version = version
        cls.network = network
        cls.network_subnet = network_subnet
        cls.state = JobState.CREATED
        # `state` changes under `_state_lock`; kills (the server's background one and a failed setup's) don't overlap
        cls._state_lock = threading.Lock()
        cls._kill_lock = threading.Lock()

    def _transition(self, to: JobState, allowed_from: tuple[JobState, ...]) -> bool:
        with self._state_lock:
            if self.state not in allowed_from:
                return False
            self.state = to
            return True

    @asyncify()
    def kill(self):
        self.kill_sync()

    @asyncify()
    def execute(self, timeout: float = DEFAULT_TIMEOUT, *args, **kwargs):
        return self.execute_sync(timeout, **kwargs)

    def kill_sync(self):
        with self._kill_lock:
            if self.container:
                try:
                    self.container.remove(force=True)
                except docker.errors.NotFound:
                    pass
                except Exception as error:
                    # it may still be running, so its rules and network stay and keep it boxed in;
                    # `remove_stale_containers` removes it later, then the network prune and rule sweep follow
                    print('error removing container', self.language, self.version, str(error), flush=True)
                    return
                self.container = None

            # network cleanup runs even without a container (creation may have failed)
            if self.network:
                with firewall_lock.shared():
                    subnet = self.network_subnet
                    if subnet:
                        try: del_egress_block_rules(subnet)
                        except Exception: pass
                        try: del_conn_limit_rule(subnet)
                        except Exception: pass
                        try: del_host_block_rule(subnet)
                        except Exception: pass
                    try: del_bandwidth_limit(self.network.id)
                    except Exception: pass
                    # nothing is attached anymore, a network left behind (busy daemon) is pruned within minutes
                    try: self.network.remove()
                    except Exception: pass
                self.network = None

            with self._state_lock:
                self.state = JobState.KILLED

    def execute_sync(
        self,
        timeout: float = DEFAULT_TIMEOUT,
        max_file_size_total: int = ULIMIT_FILE_SIZE,
        *args,
        deadline: Optional[float] = None,
        kill: bool = True,
        **kwargs,
    ):
        '''
        Runs the code for up to `timeout` seconds, or until `deadline` (a `time.time()`) when there is one, so the time it
        took to get here (the server's request, `create_job`'s setup) counts too. The timeout error says `timeout` either
        way. Without `kill` the caller removes the container (and its network) itself, after it has answered
        '''
        if not self._transition(JobState.RUNNING, (JobState.CREATED,)):
            raise Exception('Container is killed' if self.state is JobState.KILLED else f'Job already {self.state.value}')

        now = time.time()
        wait = timeout if deadline is None else deadline - now

        try:
            if wait <= 0:
                # the setup used all of it, the code never started
                print('timeout before start', self.language, self.version, flush=True)
                raise ExecutionTimeout(timeout)

            self.container.start()

            try:
                waited = self.container.wait(timeout=wait)
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as wait_error:
                # over a unix socket a read timeout comes back as a ConnectionError, over tcp as a ReadTimeout;
                # any other ConnectionError is the daemon being unreachable, not the code being slow
                if not isinstance(wait_error, requests.exceptions.ReadTimeout) and 'timed out' not in str(wait_error).lower():
                    raise
                print('timeout', self.language, self.version, f'{wait:.1f}s of {timeout:g}s', flush=True)
                raise ExecutionTimeout(timeout) from wait_error

            print('done execution', self.language, self.version, int((time.time() - now) * 1000), flush=True)

            # the entrypoint exits with the compile step's status when that failed, else the run's (a script's own exit
            # status, so a bash script that ends in a passing command is 0 even when an earlier one failed). killed by
            # the kernel (oom, fsize) is 128 + the signal. None when docker didn't say
            exit_code = waited.get('StatusCode') if isinstance(waited, dict) else None
            if not isinstance(exit_code, int):
                exit_code = None

            output = self.container.logs(stdout=True, stderr=False)
            error = self.container.logs(stdout=False, stderr=True)

            files_output: list[dict] = []
            try:
                bits, stat = self.container.get_archive(DIRECTORY_HOME_OUTPUT)
                print(stat, flush=True)

                # streamed, so a huge /output is never buffered whole and reading stops at a limit
                tar = tarfile.open(fileobj=io.BufferedReader(_ChunkReader(bits)), mode='r|')

                file_size_total = 0
                for member in tar:
                    if MAX_FILES <= len(files_output):
                        break

                    if not member.isfile():
                        continue

                    if max_file_size_total < file_size_total + member.size:
                        break

                    member_stream = tar.extractfile(member)
                    buffer = member_stream.read() if member_stream else b''
                    size = len(buffer)
                    if max_file_size_total < file_size_total + size:
                        break

                    file_size_total += size
                    files_output.append({
                        'buffer': buffer,
                        'filename': member.name.split('/')[-1],
                        'size': size,
                    })
            except:
                # incase they delete the output folder
                pass
        finally:
            # a kill from another thread (the caller hung up) may have gotten here first, KILLED stays then
            self._transition(JobState.FINISHED, (JobState.RUNNING,))
            if kill:
                self.kill_sync()

        return {
            'language': self.language.to_dict(),
            'result': {
                'error': error.decode(errors='replace').strip()[:MAX_RESULT_LENGTH],
                'exit_code': exit_code,
                'files': files_output,
                'output': output.decode(errors='replace').strip()[:MAX_RESULT_LENGTH],
            },
            'took': int((time.time() - now) * 1000),
            'version': self.version,
        }
