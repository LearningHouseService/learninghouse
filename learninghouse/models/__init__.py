from pydantic import BaseModel


class LearningHouseVersions(BaseModel):
    service: str
    sklearn: str
    numpy: str
    pandas: str

    @property
    def libraries_versions(self) -> str:
        return f'Libraries scikit-learn: {self.sklearn}, ' + \
            f'numpy: {self.numpy}, pandas: {self.pandas}'


class LearningHouseErrorMessage(BaseModel):
    error: str
    description: str = ''
