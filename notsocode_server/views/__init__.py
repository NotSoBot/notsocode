from sanic import Blueprint

from .build import build
from .execute import execute
from .languages import languages



latest = Blueprint.group(
    build,
    execute,
    languages,
)


v1 = Blueprint.group(
    *[blueprint.copy(f'v1-{blueprint.name}') for blueprint in latest.blueprints],
    version=1,
)


__all__ = (
    'latest',
    'v1',
)
