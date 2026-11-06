import asyncio
import base64
import os

from sanic import Blueprint, Request
from sanic.exceptions import SanicException
from sanic.response import json

from notsocode import Job, NotSoCode

from ..utilities.params import parse_params
from ..validators.models.execute import Execute



execute = Blueprint('execute', url_prefix='/execute')

# each job can take NOTSOCODE_PROCESS_MAX_MEMORY and NOTSOCODE_PROCESS_MAX_CPUS, this keeps the total under the host's
MAX_JOBS = int(os.getenv('NOTSOCODE_MAX_JOBS', 8))
# how long a run waits for a free slot before it's turned away with a 503
QUEUE_TIMEOUT = float(os.getenv('NOTSOCODE_QUEUE_TIMEOUT', 5))
jobs = asyncio.Semaphore(MAX_JOBS)


async def kill_and_release(job: Job):
    # the slot frees once the container is gone, a timed out one is still running until then
    try:
        await job.kill()
    finally:
        jobs.release()


@execute.post('')
@parse_params(Execute)
async def execute_script(request: Request, params=Execute):
    files = []
    if request.files:
        for storages in request.files.values():
            for storage in storages:
                files.append({
                    'buffer': storage.body,
                    'filename': storage.name,
                })

    # rename duplicates to `name (1).ext`, `name (2).ext`; no extension (or a dotfile) gets `name (1)`
    filenames: set[str] = set()
    for file_ in files:
        filename = file_['filename']
        stem, _, extension = filename.rpartition('.')

        count = 0
        while file_['filename'] in filenames:
            count += 1
            file_['filename'] = f'{stem} ({count}).{extension}' if stem else f'{filename} ({count})'
        filenames.add(file_['filename'])

    # the timeout is only the code's, it starts with the container. Waiting for a slot has its own limit instead, so
    # the setup stays inside the extra time the caller gives on top of the timeout (notsobot.api's is 10 seconds)
    try:
        await asyncio.wait_for(jobs.acquire(), timeout=QUEUE_TIMEOUT)
    except asyncio.TimeoutError:
        raise SanicException(f'Too many code runs at once ({MAX_JOBS}), try again in a bit', status_code=503)

    try:
        job = await NotSoCode.create_job(
            params.language,
            params.code,
            allow_network=params.allow_network,
            files=files,
            stdin=params.stdin,
            version=params.version,
        )
    except BaseException:
        jobs.release()
        raise
    try:
        response = await job.execute(timeout=params.timeout, kill=False)
    finally:
        # removed in the background, so the response doesn't wait on it: the container and its network (iptables/tc
        # rules too) take seconds when docker is busy. Also when the caller hung up and this got cancelled, the
        # container is killed then instead of running out its time
        request.app.add_task(kill_and_release(job))

    for i in range(len(response['result']['files'])):
        file_ = response['result']['files'][i]
        response['result']['files'][i] = {
            'filename': file_['filename'],
            'size': file_['size'],
            'value': base64.b64encode(file_['buffer']).decode(),
        }

    return json(response)
