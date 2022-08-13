from __future__ import annotations
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class LearningHouseVersions(BaseModel):
    service: str = Field(None, example='1.0.0')
    fastapi: str = Field(None, example='1.0.0')
    pydantic: str = Field(None, example='1.0.0')
    uvicorn: str = Field(None, example='1.0.0')
    sklearn: str = Field(None, example='1.0.0')
    numpy: str = Field(None, example='1.0.0')
    pandas: str = Field(None, example='1.0.0')
    jose: str = Field(None, example='1.0.0')
    passlib: str = Field(None, example='1.0.0')
    loguru: str = Field(None, example='1.0.0')

    @property
    def libraries_versions(self) -> str:
        return f'Libraries FastAPI: {self.fastapi}, uvicorn: {self.uvicorn}, ' + \
            f'pydantic: {self.pydantic}, scikit-learn: {self.sklearn}, ' + \
            f'numpy: {self.numpy}, pandas: {self.pandas}, python-jose: {self.jose}, ' +\
            f'passlib: {self.passlib}, loguru: {self.loguru}'


class LearningHouseErrorMessage(BaseModel):
    error: str
    description: str = ''


class LearningHouseValidationErrorMessage(LearningHouseErrorMessage):
    validations: List[Dict[str, Any]]

    @classmethod
    def from_error_message(cls,
                           error_message: LearningHouseErrorMessage,
                           validations: List[Dict[str, Any]]) \
            -> LearningHouseValidationErrorMessage:
        return cls(error=error_message.error,
                   description=error_message.description,
                   validations=validations)
