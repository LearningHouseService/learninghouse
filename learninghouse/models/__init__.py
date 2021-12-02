from pydantic import BaseModel


class LearningHouseVersions(BaseModel):
    service: str
    fastapi: str
    sklearn: str
    numpy: str
    pandas: str


class LearningHouseErrorMessage(BaseModel):
    error: str
    description: str = ''
