from typing import Union

from pydantic_core import PydanticCustomError



def InvalidChoiceError(choices: Union[tuple, list]) -> PydanticCustomError:
    # raised from a validator, it comes back as an `invalid_choice` error on that field
    return PydanticCustomError('invalid_choice', 'Value must be one of {choices}', {'choices': tuple(choices)})
