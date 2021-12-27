from pydantic import BaseModel


class LearningHouseVersions(BaseModel):
    service: str
    fastapi: str
    pydantic: str
    uvicorn: str
    sklearn: str
    numpy: str
    pandas: str

    @property
    def libraries_versions(self) -> str:
        return f'Libraries FastAPI: {self.fastapi}, uvicorn: {self.uvicorn}, ' + \
            f'pydantic: {self.pydantic}, scikit-learn: {self.sklearn}, ' + \
            f'numpy: {self.numpy}, pandas: {self.pandas}'


class LearningHouseErrorMessage(BaseModel):
    error: str
    description: str = ''
