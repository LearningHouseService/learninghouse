#coding: utf-8

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier


class EstimatorFactory():
    ESTIMATORS = {
        "DecisionTreeClassifier": DecisionTreeClassifier,
        "RandomForestClassifier": RandomForestClassifier
    }

    @classmethod
    def get_estimator(cls, estimatorcfg):
        options = estimatorcfg['options']

        return cls.ESTIMATORS[estimatorcfg['class']](**options)
