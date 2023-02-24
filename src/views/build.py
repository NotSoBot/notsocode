from sanic import Blueprint, Request
from sanic.response import json
from sanic_dantic import parse_params

from notsocode import NotSoCode
from utilities.constants import Languages
from validators.models.build import BuildSingle



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
    results = []
    for language in Languages:
        tested = {}
        for version in language.versions:
            tested['version'] = await NotSoCode.build_and_test(language, version=version)
        results.append({'language': language.to_dict(), 'tested': tested})
    return json(results)
