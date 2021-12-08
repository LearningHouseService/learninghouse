
from typing import List, Optional

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder


class DatasetConfiguration():
    dependent: str
    dependent_encoder: bool
    testsize: float
    imputer: SimpleImputer
    features: Optional[List[str]] = None
    columns: Optional[List[str]] = None

    def __init__(self, dependent: str, testsize: float, dependent_encode: bool):
        self.dependent = dependent
        self.testsize = testsize
        self.dependent_encoder = LabelEncoder() if dependent_encode else None
        self.imputer = SimpleImputer(missing_values=np.nan, strategy='mean')

    @property
    def dependent_encode(self) -> bool:
        return self.dependent_encoder is not None

    @property
    def has_columns(self) -> bool:
        return self.columns is not None
