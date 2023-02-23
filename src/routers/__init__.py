from urllib.parse import quote

from sanic.exceptions import NotFound
from sanic.router import Router



class MyRouter(Router):
    def get(self, path, *args, **kwargs):
        try:
            return super().get(path, *args, **kwargs)
        except NotFound:
            return super().get(quote(path), *args, **kwargs)
