from sanic import Blueprint, Request
from sanic.response import json

from utilities.constants import Languages



languages = Blueprint('languages', url_prefix='/languages')


@languages.get('')
async def get_languages(request: Request):
    result = []
    for language in Languages:
        result.append(language.to_dict())
    return json(result)
