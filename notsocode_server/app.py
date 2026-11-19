import asyncio
import hmac
import os
import time
import traceback

from dotenv import load_dotenv
from pydantic import ValidationError
from sanic import HTTPResponse, Sanic, Request
from sanic.exceptions import SanicException
from sanic.response import json

from notsocode import ExecutionTimeout, ImageBuilding, NotSoCode
from notsocode.notsocode import BUILD_WAIT, MAX_STORAGE_SIZE, MAX_TIMEOUT
from notsocode_server.routers import MyRouter
from notsocode_server.utilities.constants import HTTP_STATUS_CODES
from notsocode_server.views import latest, v1
from notsocode_server.views.build import BUILD_ALL_WAIT
from notsocode_server.views.execute import QUEUE_TIMEOUT, cleanups, print_timings



load_dotenv()


app = Sanic('notsocode', router=MyRouter())
# sanic answers a handler that runs past this with its own 503 and cancels it. Above the longest run (slot wait, image
# wait, the code's max timeout and reading its output) and the build-all long poll, so those answer for themselves
app.config.RESPONSE_TIMEOUT = int(max(QUEUE_TIMEOUT + BUILD_WAIT + MAX_TIMEOUT + 30, BUILD_ALL_WAIT + 10))

app.blueprint(latest)
app.blueprint(v1)


@app.before_server_start
async def check_docker(app: Sanic):
    # refuses to start without docker or the DOCKER-USER chain, instead of failing every run later. Also removes the job
    # containers an earlier process left behind (crashed, or stopped mid-run)
    loop = asyncio.get_running_loop()
    client = await loop.run_in_executor(None, NotSoCode.get_client)
    await loop.run_in_executor(None, NotSoCode.remove_stale_containers, client)


@app.after_server_stop
async def finish_cleanups(app: Sanic):
    # containers still being removed in the background, so a restart doesn't leave them running. A moment first: runs
    # sanic just aborted only reach their `finally` (which queues their kill) a few loop turns later. Whatever is still
    # missed, the next start's stale container sweep removes
    await asyncio.sleep(0.5)
    if cleanups:
        print(f'waiting on {len(cleanups)} job cleanups', flush=True)
        await asyncio.wait(set(cleanups), timeout=30)


@app.on_request
def before_request(request: Request):
    request.ctx.started = time.time()
    secret = os.getenv('SECRET')
    if not secret:
        raise SanicException('Secret required in environment variables', status_code=500)
    # constant-time, so the secret can't be guessed byte by byte from response timing
    authorization = request.headers.get('authorization') or ''
    if not hmac.compare_digest(authorization.encode(), secret.encode()):
        raise SanicException(status_code=403)


@app.on_response
async def after_request(request: Request, response: HTTPResponse):
    if hasattr(request.ctx, 'started'):
        started = request.ctx.started
        response.headers.add('x-took', int((time.time() - started) * 1000))
    # only /execute sets timings, error responses (408 timeouts, 503 full queue) come through here too
    print_timings(request, response.status, len(response.body or b''))
    return response


@app.exception(Exception)
async def catch_all_exceptions(request: Request, exception: Exception):
    print(exception, flush=True)
    traceback.print_exc()
    status = 500
    return json({'code': 0, 'message': str(exception), 'status': status}, status=status)


@app.exception(ExecutionTimeout)
async def catch_execution_timeout(request: Request, exception: ExecutionTimeout):
    # the user's code being slow is expected, so no traceback and not a 500
    status = 408
    return json({'code': 0, 'message': str(exception), 'status': status}, status=status)


@app.exception(ImageBuilding)
async def catch_image_building(request: Request, exception: ImageBuilding):
    # busy, not broken: the same answer as a full queue
    status = 503
    return json({'code': 0, 'message': str(exception), 'status': status}, status=status)


@app.exception(SanicException)
async def catch_sanic_exceptions(request: Request, exception: SanicException):
    print('sanic exception', exception, exception.message, flush=True)
    status = getattr(exception, 'status_code', 500)
    message = exception.message or str(exception) or HTTP_STATUS_CODES.get(status, '')
    return json({'code': 0, 'message': message, 'status': status}, status=status)


@app.exception(ValidationError)
async def catch_all_validation_exceptions(request: Request, exception: ValidationError):
    print('validation exception', exception, flush=True)
    errors: dict = {}
    for error in exception.errors():
        error_obj = errors
        for key in error['loc']:
            error_obj[key] = error_obj.get(key, {})
            error_obj = error_obj[key]

        error_obj['_errors'] = error_obj.get('_errors', [])
        error_obj['_errors'].append({'code': error.get('type', 'UNKNOWN'), 'message': error.get('msg', '')})

    status = 400
    response = {'code': 0, 'message': 'Invalid Form Body', 'status': status}
    if errors:
        response['errors'] = errors
    return json(response, status=status)



def start():
    if not MAX_STORAGE_SIZE:
        print(
            'warning: NOTSOCODE_PROCESS_MAX_STORAGE is off, a job can write until the docker disk is full '
            '(needs overlay2 on xfs mounted with pquota)',
            flush=True,
        )
    # one process: sanic's worker process re-imports the app by name, which fails under `python -m`,
    # and the build lock, prune throttle and job state are per-process anyway (jobs run on threads)
    app.run(host='0.0.0.0', port=8080, debug=False, single_process=True)

if __name__ == '__main__':
    start()
