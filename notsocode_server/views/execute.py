import asyncio
import base64
import os
import time

from typing import Optional

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


def print_timings(request: Request, status, size_out: Optional[int] = None):
    # one timestamped line per run: `total` is from the body having arrived to the response, the phases add up to most
    # of it and a missing one (-) is where it raised or got cancelled
    timings = getattr(request.ctx, 'timings', None)
    if timings is None:
        return
    total = int((time.time() - request.ctx.started) * 1000)
    phases = ' '.join(f'{phase}={timings.get(phase, "-")}' for phase in ('queue', 'create', 'run', 'encode'))
    print(
        time.strftime('%Y-%m-%d %H:%M:%S'),
        'execute',
        timings['language'],
        timings['version'] or '-',
        status,
        f'total={total} {phases} in={len(request.body)}B out={"-" if size_out is None else size_out}B',
        flush=True,
    )


@execute.post('')
@parse_params(Execute)
async def execute_script(request: Request, params=Execute):
    try:
        return await run_script(request, params)
    except asyncio.CancelledError:
        # the caller hung up (notsobot.api's own timeout). Sanic still turns this into a 500 that goes through
        # `after_request`, cleared so the run isn't printed twice
        print_timings(request, 'cancelled')
        request.ctx.timings = None
        raise


async def run_script(request: Request, params: Execute):
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

    # each phase's ms, printed with the request's total by `after_request` (also when a phase raised, it's missing then)
    timings: dict = {'language': params.language.name, 'version': params.version}
    request.ctx.timings = timings
    mark = time.time()

    def lap(phase: str):
        nonlocal mark
        now = time.time()
        timings[phase] = int((now - mark) * 1000)
        mark = now

    # the timeout is only the code's, it starts with the container. Waiting for a slot has its own limit instead, so
    # the setup stays inside the extra time the caller gives on top of the timeout (notsobot.api's is 10 seconds)
    try:
        await asyncio.wait_for(jobs.acquire(), timeout=QUEUE_TIMEOUT)
    except asyncio.TimeoutError:
        raise SanicException(f'Too many code runs at once ({MAX_JOBS}), try again in a bit', status_code=503)
    lap('queue')

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
    timings['version'] = job.version
    lap('create')
    try:
        response = await job.execute(timeout=params.timeout, kill=False)
    finally:
        # the code, its logs and reading /output; a timed out run stops here
        lap('run')
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

    # base64 and the json both run on the event loop, every other request waits on a big output
    result = json(response)
    lap('encode')
    return result
