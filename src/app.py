import os
import time
import traceback

from pydantic import ValidationError
from sanic import HTTPResponse, Sanic, Request
from sanic.exceptions import SanicException
from sanic.response import json

from routers import MyRouter
from utilities.constants import HTTP_STATUS_CODES
from views import latest, v1



app = Sanic('notsocode', router=MyRouter())
app.config.SANIC_DANTIC_ERROR = True

app.blueprint(latest)
#app.blueprint(v1)


@app.on_request
def before_request(request: Request):
    print(request, flush=True)
    request.ctx.started = time.time()
    if not os.getenv('SECRET'):
        raise SanicException('Secret required in environment variables', status_code=500)
    if request.headers.get('authorization') != os.getenv('SECRET'):
        raise SanicException(status_code=403)


@app.on_response
def after_request(request: Request, response: HTTPResponse):
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



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)#, single_process=True)
