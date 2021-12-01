
from typing import List, Optional

import numpy as np
from pydantic import BaseModel
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder


class DatasetConfiguration(BaseModel):
    dependent: str
    features: Optional[List[str]] = None


class PreprocessingConfiguration():
    testsize: float
    dependent_encoder: bool
    imputer: SimpleImputer
    columns: Optional[List[str]] = None

    def __init__(self, testsize: float, dependent_encode: bool):
        self.testsize = testsize
        self.dependent_encoder = LabelEncoder() if dependent_encode else None
        self.imputer = SimpleImputer(missing_values=np.nan, strategy='mean')

    @property
    def dependent_encode(self) -> bool:
        return self.dependent_encoder is not None

    @property
    def has_columns(self) -> bool:
        return self.columns is not None
