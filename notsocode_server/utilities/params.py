from functools import wraps
from typing import Any

from pydantic import BaseModel
from sanic import Request
from sanic.exceptions import BadRequest



def request_params(request: Request) -> dict[str, Any]:
    # query args, then the json body (an object) or the form fields over them; a key sent once is a value, more is a list
    params: dict[str, Any] = {key: values[0] if len(values) == 1 else values for key, values in request.args.items()}

    body = None
    if request.content_type.startswith('application/json'):
        try:
            body = request.json
        except BadRequest:
            body = None
    if isinstance(body, dict):
        params.update(body)
    elif request.form:
        params.update({key: values[0] if len(values) == 1 else values for key, values in request.form.items()})
    return params


def parse_params(model: type[BaseModel]):
    # validates the request against `model` and passes it as `params`, a ValidationError goes to the app's 400 handler
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            kwargs['params'] = model.model_validate(request_params(request))
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
