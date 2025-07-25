from typing import cast

from sanic import Blueprint, Request
from sanic.exceptions import SanicException
from sanic.response import json
from sanic_dantic import parse_params

from notsocode import Languages, NotSoCode

from ..validators.models.build import BuildSingle



build = Blueprint('build', url_prefix='/build')


@build.post('')
@parse_params(all=BuildSingle)
async def build_single(request: Request, params=BuildSingle):
    language = cast(Languages, params.language)
    tested = await NotSoCode.build_and_test(language, version=params.version)
    return json({
        'language': language.to_dict(),
        'tested': tested,
        'version': params.version or language.default_version,
    })


@build.post('/all')
async def build_all(request: Request):
    # todo: maybe use asyncio.gather? it'll hammer the cpu tho
    request.app.purge_tasks()
    try:
        request.app.get_task(name='build-all', raise_exception=True)
        return json({'task': 'pending'})
    except:
        task = request.app.add_task(_build_all_task(), name='build-all')
        if task is None:
            raise SanicException('Failed to create task', status_code=500)
    return json({'task': 'created'})


@build.get('/all')
async def build_all_results(request: Request):
    request.app.purge_tasks()
    try:
        task = request.app.get_task(name='build-all', raise_exception=True)
        if task:
            await task
            return json({'results': task.result(), 'task': 'done'})
        return json({'results': [], 'task': 'done'})
    except:
        pass
    return json({'results': [], 'task': 'none'})



async def _build_all_task():
    results = []
    for language in Languages:
        tested = {}
        for version in language.versions:
            tested[version] = await NotSoCode.build_and_test(language, version=version)
        results.append({'language': language.to_dict(), 'tested': tested})
    return results
