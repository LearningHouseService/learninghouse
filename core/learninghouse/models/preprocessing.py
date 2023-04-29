from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder

if TYPE_CHECKING:
    from learninghouse.models.brain import BrainConfiguration


class DatasetConfiguration:
    dependent_encoder: Optional[LabelEncoder] = None
    imputer: SimpleImputer
    data_size: Optional[int] = 0
    features: Optional[List[str]] = None
    columns: Optional[List[str]] = None

    def __init__(self, brain_config: BrainConfiguration):
        self.dependent_encoder = (
            LabelEncoder() if brain_config.dependent_encode else None
        )
        self.imputer = SimpleImputer(missing_values=np.nan, strategy="mean")

    @property
    def is_dependent_encoder(self) -> bool:
        return self.dependent_encoder is not None

    @property
    def has_columns(self) -> bool:
        return self.columns is not None
