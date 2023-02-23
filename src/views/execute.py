from sanic import Blueprint, Request
from sanic_dantic import parse_params

from validators.models.execute import Execute



execute = Blueprint('execute', url_prefix='/execute')


@execute.post('')
@parse_params(all=Execute)
async def execute_script(request: Request, params=Execute):
    pass