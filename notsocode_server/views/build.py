import asyncio
import os

from typing import Optional, cast

from sanic import Blueprint, Request
from sanic.exceptions import SanicException
from sanic.response import json

from notsocode import BaseImages, Languages, NotSoCode

from ..utilities.params import parse_params
from ..validators.models.build import BuildSingle
from .execute import jobs



build = Blueprint('build', url_prefix='/build')

BUILD_ALL_TASK = 'build-all'
# how long `GET /build/all` waits for the builds to finish before it answers `pending` with the results so far, under
# sanic's RESPONSE_TIMEOUT so a long build-all never turns into a 503
BUILD_ALL_WAIT = float(os.getenv('NOTSOCODE_BUILD_ALL_WAIT', 50))


async def build_and_test(language: Languages, version: Optional[str]) -> bool:
    # the image is built (minutes, the first time) without a slot, only its test run takes one like any other run
    await NotSoCode.build(language, version=version, base=BaseImages.BOOKWORM_SLIM)
    async with jobs:
        return await NotSoCode.build_and_test(language, version=version)


@build.post('')
@parse_params(BuildSingle)
async def build_single(request: Request, params=BuildSingle):
    language = cast(Languages, params.language)
    tested = await build_and_test(language, params.version)
    return json({
        'language': language.to_dict(),
        'tested': tested,
        'version': params.version or language.default_version,
    })


# `build-all` task: none -> pending (POST) -> done (results stay readable until the next POST starts it again).
# A restart forgets it (none). Its results list fills in as it goes, so a pending GET shows how far it got


@build.post('/all')
async def build_all(request: Request):
    # todo: maybe use asyncio.gather? it'll hammer the cpu tho
    request.app.purge_tasks()
    if request.app.get_task(BUILD_ALL_TASK, raise_exception=False) is not None:
        return json({'task': 'pending'})

    results: list[dict] = []
    task = request.app.add_task(_build_all_task(results), name=BUILD_ALL_TASK)
    if task is None:
        raise SanicException('Failed to create task', status_code=500)
    request.app.ctx.build_all_results = results
    return json({'task': 'created'})


@build.get('/all')
async def build_all_results(request: Request):
    # no purge here, it would drop a finished task before its results are read
    task = request.app.get_task(BUILD_ALL_TASK, raise_exception=False)
    if task is None:
        return json({'results': [], 'task': 'none'})

    results = getattr(request.app.ctx, 'build_all_results', [])
    # asyncio.wait, not `await task`: this request timing out or hanging up must not cancel the builds
    await asyncio.wait({task}, timeout=BUILD_ALL_WAIT)
    if not task.done():
        return json({'results': results, 'task': 'pending'})
    if task.cancelled():
        return json({'results': results, 'task': 'cancelled'})
    return json({'results': task.result(), 'task': 'done'})



async def _build_all_task(results: list[dict]):
    for language in Languages:
        errors = {}
        tested = {}
        for version in language.versions:
            # one broken language shouldn't lose every other result
            try:
                tested[version] = await build_and_test(language, version)
            except Exception as error:
                print(f'build-all {language}:{version} failed', str(error), flush=True)
                errors[version] = str(error)
                tested[version] = False
        results.append({'errors': errors, 'language': language.to_dict(), 'tested': tested})
    return results
