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
# a run's slot: acquire_slot -> held through setup and the run -> released once its container is gone (kill_and_release,
# or release_after_setup when the caller hung up mid-setup). Bounded, so a second release raises instead of quietly
# letting more than MAX_JOBS run
jobs = asyncio.BoundedSemaphore(MAX_JOBS)
# background removals still running, the server waits for them when it stops so no container is left behind
cleanups: set[asyncio.Task] = set()


async def acquire_slot(timeout: float) -> bool:
    # waits up to `timeout` for a slot. Not `wait_for(jobs.acquire())`: before python 3.12 that could lose a slot it got
    # just as it timed out or the request was cancelled
    acquiring = asyncio.ensure_future(jobs.acquire())
    try:
        await asyncio.wait({acquiring}, timeout=timeout)
    except BaseException:
        _drop_acquire(acquiring)
        raise
    if acquiring.done():
        return True
    _drop_acquire(acquiring)
    return False


def _drop_acquire(acquiring: asyncio.Future):
    if not acquiring.done():
        # Semaphore.acquire passes a slot it got meanwhile on to the next waiter when it's cancelled
        acquiring.cancel()
    elif not acquiring.cancelled() and acquiring.exception() is None:
        jobs.release()


def run_cleanup(coroutine):
    task = asyncio.get_running_loop().create_task(coroutine)
    cleanups.add(task)
    task.add_done_callback(cleanups.discard)
    return task


async def kill_and_release(job: Job):
    # the slot frees once the container is gone, a timed out one is still running until then
    try:
        await job.kill()
    finally:
        jobs.release()


async def release_after_setup(setup: asyncio.Future):
    # the caller hung up during `create_job`: its thread can't be stopped, so the job it makes is removed once it's done
    # and the slot stays taken until then (otherwise more than MAX_JOBS setups could run)
    try:
        job = await setup
    except BaseException:
        jobs.release()
        return
    await kill_and_release(job)


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
    if not await acquire_slot(QUEUE_TIMEOUT):
        raise SanicException(f'Too many code runs at once ({MAX_JOBS}), try again in a bit', status_code=503)
    lap('queue')

    # from here the slot is this run's until one of the cleanups below gives it back
    setup = asyncio.ensure_future(NotSoCode.create_job(
        params.language,
        params.code,
        allow_network=params.allow_network,
        files=files,
        stdin=params.stdin,
        version=params.version,
    ))
    try:
        # shielded, so a hang up doesn't drop the job the setup thread is still making
        job = await asyncio.shield(setup)
    except asyncio.CancelledError:
        run_cleanup(release_after_setup(setup))
        raise
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
        run_cleanup(kill_and_release(job))

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
