from typing import Union



class InvalidChoiceError(ValueError):
    code = 'invalid_choice'

    def __init__(self, choices: Union[tuple, list]):
        if not isinstance(choices, tuple):
            choices = tuple(choices)
        super().__init__(f'Value must be one of {choices}')
