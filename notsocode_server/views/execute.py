import base64

from sanic import Blueprint, Request
from sanic.response import json
from sanic_dantic import parse_params

from notsocode import NotSoCode

from ..validators.models.execute import Execute



execute = Blueprint('execute', url_prefix='/execute')


@execute.post('')
@parse_params(all=Execute)
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

    job = await NotSoCode.create_job(
        params.language,
        params.code,
        allow_network=params.allow_network,
        files=files,
        stdin=params.stdin,
        version=params.version,
    )
    request.ctx.jobs.add(job)
    response = await job.execute(timeout=params.timeout)
    request.ctx.jobs.remove(job)

    for i in range(len(response['result']['files'])):
        file_ = response['result']['files'][i]
        response['result']['files'][i] = {
            'filename': file_['filename'],
            'size': file_['size'],
            'value': base64.b64encode(file_['buffer']).decode(),
        }

    return json(response)
