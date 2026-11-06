from typing import Annotated, Any

from pydantic import PlainValidator

from notsocode import Languages

from .exceptions import InvalidChoiceError



def enum_by_name(enumerable: Any):
    # members are picked by name (`PYTHON`), their values are tuples nobody sends
    def validate(value: Any) -> Any:
        if isinstance(value, enumerable):
            return value
        try:
            return enumerable[value]
        except (KeyError, TypeError):
            raise InvalidChoiceError(enumerable.keys())
    return PlainValidator(validate, json_schema_input_type=str)


ValidLanguages = Annotated[Languages, enum_by_name(Languages)]
