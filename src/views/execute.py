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
    files = []
    for storages in request.files.values():
        for storage in storages:
            files.append({
                'buffer': storage.body,
                'filename': storage.name,
            })

    file_counter: dict[str, int] = {}
    for i in range(len(files)):
        file_ = files[i]
        filename = file_['filename']

        count = 0
        if filename in file_counter:
            count = file_counter[filename] + 1
            parts = filename.split('.')
            filename_new = '.'.join(parts[:-1]) + f' ({count}).{parts[-1]}'
            file_['filename'] = filename_new
        file_counter[filename] = count

    result = await NotSoCode.execute(
        params.language,
        params.code,
        version=params.version,
        files=files,
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
