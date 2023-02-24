import asyncio
import time

from sanic import Blueprint, Request
from sanic.response import json
from sanic_dantic import parse_params

from notsocode import NotSoCode
from utilities.constants import Languages
from validators.models.execute import Execute



execute = Blueprint('execute', url_prefix='/execute')


@execute.post('')
@parse_params(all=Execute)
async def execute_script(request: Request, params=Execute):
    # todo: get files from request.storage
    result = await NotSoCode.execute(
        params.language,
        params.code,
        version=params.version,
        files=[],
        stdin=params.stdin,
    )
    return json(result)


@execute.post('/test')
async def execute_script_test(request: Request):
    # todo: get files from request.storage
    futures = []
    for i in range(200):
        future = NotSoCode.execute(Languages.BASH, 'echo "OK"')
        futures.append(future)
    now = time.time()
    results = await asyncio.gather(*futures)
    return json({'results': results, 'took': int((time.time() - now) * 1000)})
