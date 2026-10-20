import hmac
import os
import time
import traceback

from dotenv import load_dotenv
from pydantic import ValidationError
from sanic import HTTPResponse, Sanic, Request
from sanic.exceptions import SanicException
from sanic.response import json

from notsocode import ExecutionTimeout
from notsocode_server.routers import MyRouter
from notsocode_server.utilities.constants import HTTP_STATUS_CODES
from notsocode_server.views import latest, v1



load_dotenv()


app = Sanic('notsocode', router=MyRouter())
app.config.SANIC_DANTIC_ERROR = True

app.blueprint(latest)
app.blueprint(v1)


@app.on_request
def before_request(request: Request):
    request.ctx.jobs = set()
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
    if hasattr(request.ctx, 'jobs'):
        for job in request.ctx.jobs:
            await job.kill()

    if hasattr(request.ctx, 'started'):
        started = request.ctx.started
        response.headers.add('x-took', int((time.time() - started) * 1000))
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
    # one process: sanic's worker process re-imports the app by name, which fails under `python -m`,
    # and the build lock, prune throttle and job state are per-process anyway (jobs run on threads)
    app.run(host='0.0.0.0', port=8080, debug=False, single_process=True)

if __name__ == '__main__':
    start()
