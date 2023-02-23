import json
import io
import os
import tarfile
import time

from typing import Optional, Union

import docker
import requests

from utilities.constants import Languages
from utilities.wrappers import asyncify



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
MAX_STORAGE_SIZE = '256m'

ULIMIT_FILE_SIZE = 100 * 1024 * 1024
ULIMIT_FILES = 2048
ULIMIT_MEMORY = 128 * 1024 * 1024
ULIMIT_PROCESSES = 128


class NotSoCode:
    client = None
    client_api = None
    dockerfiles_directory = '../dockerfiles'
    tag_prepend = 'notsocode'

    @classmethod
    def generate_tag(cls, language_: Languages, version: Optional[str] = None):
        language = language_.language
        version = version or language_.default_version
        return f'{cls.tag_prepend}-{language}-{version}'

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
    def build_sync(cls, language_: Languages, version: Optional[str] = None, **kwargs):
        print(kwargs, flush=True)
        language = language_.language
        version = version or language_.default_version
    
        directory = os.path.dirname(__file__) + os.path.join(cls.dockerfiles_directory, language, version or '')
        if not os.path.exists(directory):
            raise Exception('Invalid Build')

        kwargs['buildargs'] = {
            'DIRECTORY_HOME': DIRECTORY_HOME,
            'DIRECTORY_OUTPUT': DIRECTORY_HOME_OUTPUT,
            'MAX_FILES': str(MAX_FILES),
            'USER': os.getenv('NOTSOCODE_USER', DEFAULT_USER),
            'USER_UID': os.getenv('NOTSOCODE_USER_UID', DEFAULT_USER_UID),
        }

        client = cls.get_api_client()
        lines = [
            json.loads(x) for x in client.build(path=directory, tag=cls.generate_tag(language_), forcerm=True, **kwargs)
        ]
        print(lines, flush=True)

        if 'errorDetail' in lines[-1]:
            raise Exception('\n'.join(x.get('error', x.get('stream', '')) for x in lines))#last_line['errorDetail']['message'])
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

    # stdin https://github.com/docker/docker-py/issues/3057#issuecomment-1290140396
    @classmethod
    @asyncify()
    def execute(
        cls,
        language: Languages,
        code: str,
        version: Optional[str] = None,
        files: list[dict] = [],
        stdin: str = '',
        timeout: int = 10,
    ):
        tar_stream = cls.create_tar(
            files=[
                (code.encode(), f'{FILENAME_SCRIPT}.{language.extension}', None),
                (stdin.encode(), FILENAME_STDIN, None),
                *[(x['buffer'], DIRECTORY_INPUT + '/' + x['filename']) for x in files],
            ],
            directories=[DIRECTORY_INPUT, DIRECTORY_OUTPUT],
        )

        cls.build_sync(language, version=version)
        tag = cls.generate_tag(language, version=version)

        client = cls.get_client()
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
                #mem_limit='256m',
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

            container.start()

            try:
                container.wait(timeout=timeout)
            except requests.exceptions.ConnectionError:
                print(container.logs(stdout=True, stderr=False), flush=True)
                print(container.logs(stdout=False, stderr=True), flush=True)
                raise ValueError(f'Code Execution took longer than {timeout} seconds')

            output = container.logs(stdout=True, stderr=False)
            error = container.logs(stdout=False, stderr=True)

            files_output: list[str] = []
            try:
                bits, stat = container.get_archive(DIRECTORY_HOME_OUTPUT)
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
                    files_output.append(member.name.split('/')[-1])
                    print(member, flush=True)
            except:
                # incase they delete the output folder
                pass
        finally:
            try:
                container.remove()
            except:
                pass

        return {
            'language': language.language,
            'result': {
                'error': error.decode().strip(),
                'files': files_output,
                'output': output.decode().strip(),
            },
            'version': version or language.default_version,
        }