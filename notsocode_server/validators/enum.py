from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any, Union

from notsocode import Languages

from .exceptions import InvalidChoiceError



class ValidEnums:
    __enumerable__: Any

    @classmethod
    def __get_validators__(cls) -> Iterator[Callable[..., Any]]:
        yield cls.validate

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema: dict[str, object]) -> None:
        field_schema.update(enum=cls.__enumerable__.keys())

    @classmethod
    def validate(cls, value: str, _ = None) -> Any:
        try:
            return cls.__enumerable__[value]
        except:
            raise InvalidChoiceError(cls.__enumerable__.keys())



class ValidLanguages(ValidEnums):
    __enumerable__ = Languages
