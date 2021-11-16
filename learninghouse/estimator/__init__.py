#coding: utf-8

from typing import Optional

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor



class EstimatorFactory():
    ESTIMATORS = {
        "regressor": RandomForestRegressor,
        "classifier": RandomForestClassifier
    }

    @classmethod
    def get_estimator(cls, typed, estimators=100, max_depth=5, random_state=0):
        estimatorcfg = {
            "typed": typed,
            "estimators": 100,
            "max_depth": max_depth,
            "random_state": random_state
        }

        return cls.ESTIMATORS[typed](n_estimators=estimators,
                                     max_depth=max_depth,
                                     random_state=random_state), estimatorcfg
