from sanic import Blueprint, Request
from sanic_dantic import parse_params

from notsocode import NotSoCode
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
