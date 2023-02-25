from pydantic import BaseModel as PydanticBaseModel, Field, validator

from ..exceptions import InvalidChoiceError

from ..enum import ValidLanguages



class BaseModel(PydanticBaseModel):
    class Config:
        anystr_strip_whitespace = True


class BaseLanguage(BaseModel):
    language: ValidLanguages
    version: str = Field(default='')

    @validator('version', always=True)
    def version_must_be_in_language(cls, value: str, values: dict):
        if 'language' not in values:
            return ''

        language = values['language']
        if not value:
            return language.default_version

        if value not in language.versions:
            raise InvalidChoiceError(language.versions)
        return value
