from __future__ import annotations

from typing import TYPE_CHECKING

import json
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from learninghouse import logger

if TYPE_CHECKING:
    from learninghouse.brain import BrainConfiguration


class DatasetPreprocessing():
    SENSORCONFIG_FILE = 'brain/config/sensors.json'
    CATEGORICAL_KEY = 'categorical'
    NUMERICAL_KEY = 'numerical'

    @classmethod
    def sensorsconfig(cls):
        categoricals = []
        numericals = []

        with open(cls.SENSORCONFIG_FILE, 'r', encoding='utf-8') as json_file:
            sensors = json.load(json_file)
            categoricals = list(map(lambda x: x[0], filter(
                lambda x: x[1] == cls.CATEGORICAL_KEY, sensors.items())))
            numericals = list(map(lambda x: x[0], filter(
                lambda x: x[1] == cls.NUMERICAL_KEY, sensors.items())))

        categoricals.append('month_of_year')
        numericals.append('day_of_month')
        categoricals.append('day_of_week')
        numericals.append('hour_of_day')
        numericals.append('minute_of_hour')

        logger.debug('Sensors config: %s, %s', categoricals, numericals)

        return categoricals, numericals

    @staticmethod
    def add_time_information(data: pd.DataFrame):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().timestamp()

        date = datetime.fromtimestamp(data['timestamp'])
        data['datetime'] = date.strftime('%Y-%m-%d %H:%M:%s')
        data['month_of_year'] = date.month
        data['day_of_month'] = date.day
        data['day_of_week'] = date.strftime('%A')
        data['hour_of_day'] = date.hour
        data['minute_of_hour'] = date.minute

        return data

    @classmethod
    def get_x_selected_and_numerical_columns(cls, brain: BrainConfiguration, data):
        categoricals, numericals = cls.sensorsconfig()

        categoricals = cls.columns_intersection(categoricals, data)

        if len(categoricals) > 0:
            used_columns = categoricals + \
                cls.columns_intersection(numericals, data)

            x_temp = pd.get_dummies(data[used_columns], columns=categoricals)

            features_in_dataframe = cls.columns_intersection(
                x_temp, brain.dataset.features)

            x_selected = x_temp[features_in_dataframe]
        else:
            features_in_dataframe = cls.columns_intersection(
                data, brain.dataset.features)

            x_selected = data[features_in_dataframe]

        x_selected = cls.sort_columns(x_selected)

        return x_selected, numericals

    @classmethod
    def prepare_training(cls, brain: BrainConfiguration, data: pd.DataFrame):
        x_vector, numericals = cls.get_x_selected_and_numerical_columns(
            brain, data)

        y_vector = data[brain.dataset.dependent]

        if brain.preprocessing.dependent_encode:
            y_vector = brain.preprocessing.dependent_encoder.fit_transform(
                y_vector)

        x_train, x_test, y_train, y_test = train_test_split(
            x_vector, y_vector, test_size=brain.preprocessing.testsize, random_state=0)

        numericals = cls.columns_intersection(
            numericals, brain.dataset.features)

        x_train = DatasetPreprocessing.transform_columns(
            brain.preprocessing.imputer.fit_transform, x_train, numericals)
        x_test = DatasetPreprocessing.transform_columns(
            brain.preprocessing.imputer.transform, x_test, numericals)

        x_train = cls.sort_columns(x_train)
        x_test = cls.sort_columns(x_test)

        return brain, x_train, x_test, y_train, y_test

    @classmethod
    def prepare_prediction(cls, modelcfg, data):
        x_vector, numericals = cls.get_x_selected_and_numerical_columns(
            modelcfg, data)

        numericals = cls.columns_intersection(
            modelcfg.columns.tolist(), numericals)

        missing_columns = set.difference(cls.set_of_columns(
            numericals), cls.set_of_columns(x_vector))

        for missing_column in missing_columns:
            x_vector.insert(0, missing_column, [np.nan])

        x_vector = x_vector.reindex(columns=modelcfg.columns, fill_value=0)
        x_vector = cls.sort_columns(x_vector)

        x_vector = DatasetPreprocessing.transform_columns(
            modelcfg.imputer.transform, x_vector, numericals)

        if modelcfg.has_standard_scaled():
            x_vector = DatasetPreprocessing.transform_columns(
                modelcfg.standard_scaler.transform, x_vector, modelcfg.standard_scaled)

        return cls.sort_columns(x_vector)

    @staticmethod
    def transform_columns(func, data, columns):
        data_temp = data.copy()
        data_temp[columns] = func(data[columns])
        return data_temp

    @staticmethod
    def sort_columns(data):
        data_temp = data.copy()
        return data_temp.reindex(sorted(data.columns), axis=1)

    @classmethod
    def columns_intersection(cls, list_or_dataframe1, list_or_dataframe2):
        set1 = cls.set_of_columns(list_or_dataframe1)
        set2 = cls.set_of_columns(list_or_dataframe2)
        return sorted(list(set.intersection(set1, set2)))

    @staticmethod
    def set_of_columns(list_or_dataframe):
        set_of_columns = None
        if isinstance(list_or_dataframe, pd.DataFrame):
            set_of_columns = set(list_or_dataframe.columns.values.tolist())
        elif isinstance(list_or_dataframe, list):
            set_of_columns = set(list_or_dataframe)

        return set_of_columns
