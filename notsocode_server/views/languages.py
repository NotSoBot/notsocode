from typing import cast

from sanic import Blueprint, Request
from sanic.response import json
from sanic_dantic import parse_params

from notsocode import Languages, NotSoCode

from ..validators.models.language import LanguageExample



languages = Blueprint('languages', url_prefix='/languages')


@languages.get('')
async def get_languages(request: Request):
    result = []
    for language in Languages:
        result.append(language.to_dict())
    return json(result)


@languages.get('/example')
@parse_params(all=LanguageExample)
async def get_language_example(request: Request, params: LanguageExample):
    language = cast(Languages, params.language)
    code = await NotSoCode.get_example_code(language, version=params.version)
    return json({
        'code': code,
        'language': language.to_dict(),
        'version': params.version or language.default_version,
    })
