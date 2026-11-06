from pydantic import BaseModel as PydanticBaseModel, ConfigDict, Field, ValidationInfo, field_validator

from ..exceptions import InvalidChoiceError

from ..enum import ValidLanguages



class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class BaseLanguage(BaseModel):
    language: ValidLanguages
    # validated even when left out, so it ends up as the language's default
    version: str = Field(default='', validate_default=True)

    @field_validator('version')
    @classmethod
    def version_must_be_in_language(cls, value: str, info: ValidationInfo):
        if 'language' not in info.data:
            return ''

        language = info.data['language']
        if not value:
            return language.default_version

        if value not in language.versions:
            raise InvalidChoiceError(language.versions)
        return value
