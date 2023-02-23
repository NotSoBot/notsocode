from sanic import Blueprint, Request
from sanic.response import json
from sanic_dantic import parse_params

from api.notsocode import NotSoCode
from utilities.constants import Languages
from validators.models.build import BuildSingle



build = Blueprint('build', url_prefix='/build')


@build.post('')
@parse_params(all=BuildSingle)
async def build_single(request: Request, params=BuildSingle):
    await NotSoCode.build(params.language, version=params.version)
    return json({
        'language': params.language.to_dict(),
        'version': params.version or params.language.version,
    })


@build.post('/all')
async def build_all(request: Request):
    # todo: maybe use asyncio.gather? it'll hammer the cpu tho
    for language in Languages:
        for version in language.versions:
            await NotSoCode.build(language, version=version)
    return json([language.to_dict() for language in Languages])
