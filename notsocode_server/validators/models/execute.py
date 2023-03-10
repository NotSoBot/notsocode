from pydantic import Field

from notsocode import DEFAULT_TIMEOUT

from .base import BaseLanguage



class Execute(BaseLanguage):
    code: str = Field(min_length=1, max_length=4 * 1024 * 1024)
    stdin: str = Field(default='', max_length=8 * 1024 * 1024)
    timeout: int = Field(default=DEFAULT_TIMEOUT)
