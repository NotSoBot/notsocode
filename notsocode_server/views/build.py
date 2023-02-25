from sanic import Blueprint, Request
from sanic.response import json
from sanic_dantic import parse_params

from notsocode import Languages, NotSoCode

from ..validators.models.build import BuildSingle



build = Blueprint('build', url_prefix='/build')


@build.post('')
@parse_params(all=BuildSingle)
async def build_single(request: Request, params=BuildSingle):
    tested = await NotSoCode.build_and_test(params.language, version=params.version)
    return json({
        'language': params.language.to_dict(),
        'tested': tested,
        'version': params.version or params.language.version,
    })


@build.post('/all')
async def build_all(request: Request):
    # todo: maybe use asyncio.gather? it'll hammer the cpu tho
    request.app.purge_tasks()
    try:
        task = request.app.get_task('build-all')
        return json({'task': 'pending'})
    except:
        task = request.app.add_task(_build_all_task(), name='build-all')
    return json({'task': 'created'})


@build.get('/all')
async def build_all_results(request: Request):
    request.app.purge_tasks()
    try:
        task = request.app.get_task('build-all')
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
