import json
import io
import os
import tarfile
import time

from typing import Any, Optional, Union

import docker
import requests

from notsocode.utilities.constants import BaseImages, Languages
from notsocode.utilities.wrappers import asyncify



DEFAULT_USER = 'notsocoder'
DEFAULT_USER_UID = '42069'

DIRECTORY_INPUT = '/input'
DIRECTORY_OUTPUT = '/output'

DIRECTORY_HOME = '/home/notsocoder'
DIRECTORY_HOME_INPUT = DIRECTORY_HOME + DIRECTORY_INPUT
DIRECTORY_HOME_OUTPUT = DIRECTORY_HOME + DIRECTORY_OUTPUT
FILENAME_SCRIPT = 'script'
FILENAME_STDIN = 'stdin'

MAX_FILES = 10
MAX_MEMORY = '256m'
MAX_RESULT_LENGTH = 1 * 1024 * 1024
MAX_STORAGE_SIZE = '256m'

ULIMIT_FILE_SIZE = 100 * 1024 * 1024
ULIMIT_FILES = 2048
ULIMIT_MEMORY = 128 * 1024 * 1024
ULIMIT_PROCESSES = 128


class NotSoCode:
    BUILD_STATUS: dict[str, bool] = {}

    client = None
    client_api = None
    dockerfiles_directory = '/dockerfiles'
    tag_prepend = 'notsocode'

    @classmethod
    def generate_tag(cls, language_: Languages, version: Optional[str] = None):
        language = language_.language
        version = version or language_.default_version
        return f'{cls.tag_prepend}-{language}:{version}'

    @classmethod
    def get_api_client(cls):
        if not cls.client_api:
            cls.client_api = docker.APIClient(base_url=os.getenv('DOCKER_BASE_URL'))
        return cls.client_api

    @classmethod
    def get_client(cls):
        if not cls.client:
            if os.getenv('DOCKER_BASE_URL'):
                cls.client = docker.DockerClient(base_url=os.getenv('DOCKER_BASE_URL'))
            else:
                cls.client = docker.from_env()
        return cls.client

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

        if base is not None:
            cls.build_base_sync(base)

        return cls._build_sync(directory, cls.generate_tag(language_, version=version), base=base, **kwargs)

    @classmethod
    def build_base_sync(cls, base: BaseImages, **kwargs):
        if base != BaseImages.BUILDER:
            cls.build_base_sync(BaseImages.BUILDER)
        directory = os.path.dirname(__file__) + os.path.join(cls.dockerfiles_directory, base.value[0], base.value[1])
        return cls._build_sync(directory, tag=base.tag)

    @classmethod
    def _build_sync(cls, directory: str, tag: str, base: Optional[BaseImages] = None, **kwargs):
        if tag in cls.BUILD_STATUS:
            if not cls.BUILD_STATUS[tag]:
                raise Exception(f'{tag} is currently being built, come back later')
            return

        cls.BUILD_STATUS[tag] = False
        kwargs['buildargs'] = {
            'BASE_IMAGE': base.tag if base else BaseImages.BUSTER.tag,
            'DIRECTORY_HOME': DIRECTORY_HOME,
            'DIRECTORY_OUTPUT': DIRECTORY_HOME_OUTPUT,
            'MAX_FILES': str(MAX_FILES),
            'USER': os.getenv('NOTSOCODE_USER', DEFAULT_USER),
            'USER_UID': os.getenv('NOTSOCODE_USER_UID', DEFAULT_USER_UID),
        }
 
        print(f'Building {tag}.', flush=True)
        client = cls.get_api_client()
        lines = [
            json.loads(x) for x in client.build(path=directory, tag=tag, forcerm=True, **kwargs)
        ]
        print(lines, flush=True)

        if 'errorDetail' in lines[-1]:
            del cls.BUILD_STATUS[tag]
            raise Exception('\n'.join(x.get('error', x.get('stream', '')) for x in lines))#last_line['errorDetail']['message'])

        cls.BUILD_STATUS[tag] = True
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
        extension = language_.extension
        language = language_.language
        extension = language_.extension
        version = version or language_.default_version
        filepath = os.path.dirname(__file__) + os.path.join(cls.dockerfiles_directory, language, version or '', f'test.{extension}')
        if not os.path.exists(filepath):
            raise Exception(f'Test for {cls.generate_tag(language_, version=version)} does not exist.')
    
        with open(filepath, 'r') as f:
            code = f.read()

        job = cls.create_job_sync(language_, code, version=version)
        result = job.execute_sync()
        return result['result']['output'] == 'OK'

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
    ):
        now = time.time()
        tar_stream = cls.create_tar(
            files=[
                (code.encode(), f'{FILENAME_SCRIPT}.{language.extension}'),
                (stdin.encode(), FILENAME_STDIN),
                *[(x['buffer'], DIRECTORY_INPUT + '/' + x['filename']) for x in files],
            ],
            directories=[DIRECTORY_INPUT, DIRECTORY_OUTPUT],
        )

        cls.build_sync(language, version=version, base=BaseImages.BUSTER_SLIM)
        tag = cls.generate_tag(language, version=version)

        client = cls.get_client()

        job = Job(None, language, version=version or language.default_version)
        try:
            # todo: add memory and storage limits, then limit cpu
            container = client.containers.create(
                tag,
                # cpu limits
                #cpu_period=1,
                #cpu_quota=1,
                #cpu_rt_period=1,
                #cpu_rt_runtime=1,
                #cpu_shares=1,
                detach=True,
                # device read/write limits
                #kernel_memory=1,
                log_config=docker.types.LogConfig(config={
                    'max-size': str(MAX_RESULT_LENGTH * 2),
                }),
                mem_limit=max_memory,
                #mounts=[
                #    docker.types.Mount(
                #        target='/home',
                #        source=directory,
                #        type='bind',
                #        #driver_config=docker.types.DriverConfig('local', options={'size': MAX_STORAGE_SIZE}),
                #    ),
                #],
                #nano_cpus=1,
                network_disabled=True,
                network_mode='none',
                #user=os.getenv('NOTSOCODE_USER'),
                #tmpfs={
                #    f'{DIRECTORY_HOME}{DIRECTORY_OUTPUT}': 'size=100m',
                #},
                #stdin_open=bool(stdin),
                #storage_opt={'size': '128m'},
                #tty=bool(stdin),
                ulimits=[
                    #docker.types.Ulimit(name='as', soft=ULIMIT_MEMORY, hard=ULIMIT_MEMORY),
                    docker.types.Ulimit(name='fsize', soft=ULIMIT_FILE_SIZE, hard=ULIMIT_FILE_SIZE),
                    docker.types.Ulimit(name='nofile', soft=ULIMIT_FILES, hard=ULIMIT_FILES),
                    docker.types.Ulimit(name='nproc', soft=ULIMIT_PROCESSES, hard=ULIMIT_PROCESSES),
                ],
            )

            tar_stream.seek(0)
            container.put_archive(DIRECTORY_HOME, tar_stream)

            job.container = container
        except:
            job.container = None

        print('done creation', int((time.time() - now) * 1000), flush=True)
        return job

    @classmethod
    @asyncify()
    def execute(cls, *args, **kwargs):
        return cls.execute_sync(*args, **kwargs)

    @classmethod
    def execute_sync(cls, *args, **kwargs):
        job = cls.create_job_sync(*args, **kwargs)
        return job.execute_sync()


class Job:
    def __init__(
        cls,
        container: Any,
        language: Languages,
        version: str,
    ):
        cls.container = container
        cls.language = language
        cls.version = version

    @asyncify()
    def kill(self):
        self.kill_sync()

    @asyncify()
    def execute(self, timeout: int = 10):
        return self.execute_sync(timeout)

    def kill_sync(self):
        if not self.container:
            return
        try:
            self.container.remove(force=True)
        except:
            pass
        self.container = None

    def execute_sync(self, timeout: int = 10):
        if not self.container:
            raise Exception('Container is killed')

        now = time.time()

        try:
            self.container.start()

            try:
                self.container.wait(timeout=timeout)
            except requests.exceptions.ConnectionError:
                print(self.container.logs(stdout=True, stderr=False), flush=True)
                print(self.container.logs(stdout=False, stderr=True), flush=True)
                raise ValueError(f'Code Execution took longer than {timeout} seconds')

            print('done execution', int((time.time() - now) * 1000), flush=True)

            output = self.container.logs(stdout=True, stderr=False)
            error = self.container.logs(stdout=False, stderr=True)

            files_output: list[dict] = []
            try:
                bits, stat = self.container.get_archive(DIRECTORY_HOME_OUTPUT)
                print(stat, flush=True)

                tar_stream = io.BytesIO()
                for chunk in bits:
                    tar_stream.write(chunk)

                tar_stream.seek(0)
                tar = tarfile.open(fileobj=tar_stream, mode='r')

                # todo: output the files correctly
                for member in tar.getmembers():
                    if not member.isfile():
                        continue

                    member_stream = tar.extractfile(member)
                    buffer = member_stream.read() if member_stream else b''
                    files_output.append({
                        'buffer': buffer,
                        'filename': member.name.split('/')[-1],
                        'size': len(buffer),
                    })
            except:
                # incase they delete the output folder
                pass
        finally:
            try:
                self.container.remove()
            except:
                pass

        return {
            'language': self.language.language,
            'result': {
                'error': error.decode().strip()[:MAX_RESULT_LENGTH],
                'files': files_output,
                'output': output.decode().strip()[:MAX_RESULT_LENGTH],
            },
            'took': int((time.time() - now) * 1000),
            'version': self.version,
        }
