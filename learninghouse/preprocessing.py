from __future__ import annotations

import json
import time
from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from . import logger


class DatasetPreprocessing():
    SENSORCONFIG_FILE = 'models/config/sensors.json'
    CATEGORICAL_KEY = 'categorical'

    @classmethod
    def sensorsconfig(cls):
        categoricals = []
        non_categoricals = []

        with open(cls.SENSORCONFIG_FILE, 'r', encoding='utf-8') as json_file:
            sensors = json.load(json_file)
            categoricals = list(map(lambda x: x[0], filter(
                lambda x: x[1] == cls.CATEGORICAL_KEY, sensors.items())))
            non_categoricals = list(map(lambda x: x[0], filter(
                lambda x: x[1] != cls.CATEGORICAL_KEY, sensors.items())))

        categoricals.append('day_of_week')
        categoricals.append('month_of_year')

        return categoricals, non_categoricals

    @staticmethod
    def add_time_information(data):
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
    def get_x_and_non_categoricals(cls, modelcfg, df):
        categoricals, non_categoricals = cls.sensorsconfig()

        categoricals = cls.columns_intersection(categoricals, df)

        if len(categoricals) > 0:
            used_columns = categoricals + \
                cls.columns_intersection(non_categoricals, df)

            x_temp = pd.get_dummies(df[used_columns], columns=categoricals)

            features_in_dataframe = cls.columns_intersection(
                x_temp, modelcfg.features)

            x = x_temp[features_in_dataframe]
        else:
            features_in_dataframe = cls.columns_intersection(
                df, modelcfg.features)

            x = df[features_in_dataframe]

        return x, non_categoricals

    @classmethod
    def prepare_training(cls, modelcfg, df: pd.DataFrame):
        x, non_categoricals = cls.get_x_and_non_categoricals(modelcfg, df)

        y = df[modelcfg.dependent]

        if modelcfg.dependent_encode:
            y = modelcfg.dependent_encoder.fit_transform(y)

        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=modelcfg.testsize, random_state=0)

        non_categoricals = cls.columns_intersection(
            non_categoricals, modelcfg.features)

        x_train = DatasetPreprocessing.transform_columns(
            modelcfg.imputer.fit_transform, x_train, non_categoricals)
        x_test = DatasetPreprocessing.transform_columns(
            modelcfg.imputer.transform, x_test, non_categoricals)

        if modelcfg.has_standard_scaled():
            if not modelcfg.standard_scaler_fitted:
                x_train = DatasetPreprocessing.transform_columns(
                    modelcfg.standard_scaler.fit_transform, x_train, modelcfg.standard_scaled)
                modelcfg.standard_scaler_fitted = True

            x_test = DatasetPreprocessing.transform_columns(
                modelcfg.standard_scaler.transform, x_test, modelcfg.standard_scaled)

        return modelcfg, x_train, x_test, y_train, y_test

    @classmethod
    def prepare_prediction(cls, modelcfg, df):
        x, non_categoricals = cls.get_x_and_non_categoricals(modelcfg, df)

        non_categoricals = list(set.intersection(
            set(modelcfg.columns), set(non_categoricals)))

        for missing_column in set.difference(cls.set_of_columns(non_categoricals), cls.set_of_columns(x)):
            x.insert(0, missing_column, [np.nan])

        x = DatasetPreprocessing.transform_columns(
            modelcfg.imputer.transform, x, non_categoricals)

        x = x.reindex(columns=modelcfg.columns, fill_value=0)

        if modelcfg.has_standard_scaled():
            x = DatasetPreprocessing.transform_columns(
                modelcfg.standard_scaler.transform, x, modelcfg.standard_scaled)

        return x

    @staticmethod
    def transform_columns(func, df, columns):
        df_temp = df.copy()
        df_temp[columns] = func(df[columns])
        return df_temp

    @classmethod
    def columns_intersection(cls, list_or_dataframe1, list_or_dataframe2):
        set1 = cls.set_of_columns(list_or_dataframe1)
        set2 = cls.set_of_columns(list_or_dataframe2)
        return list(set.intersection(set1, set2))

    @staticmethod
    def set_of_columns(list_or_dataframe):
        set_of_columns = None
        if isinstance(list_or_dataframe, pd.DataFrame):
            set_of_columns = set(list_or_dataframe.columns.values.tolist())
        elif isinstance(list_or_dataframe, list):
            set_of_columns = set(list_or_dataframe)

        return set_of_columns
