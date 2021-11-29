#coding: utf-8

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from learninghouse.estimator.api import EstimatorConfiguration


class EstimatorFactory():
    ESTIMATORS = {
        "regressor": RandomForestRegressor,
        "classifier": RandomForestClassifier
    }

    @classmethod
    def get_estimator(cls, configuration: EstimatorConfiguration):
        return cls.ESTIMATORS[configuration.typed](n_estimators=configuration.estimators,
                                                   max_depth=configuration.max_depth,
                                                   random_state=configuration.random_state)
