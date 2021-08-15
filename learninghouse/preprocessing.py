import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

import time
from datetime import datetime


class DatasetPreprocessing():
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

    @staticmethod
    def prepare_training(modelcfg, df):
        if modelcfg.has_categoricals():
            x = pd.get_dummies(df[modelcfg.features],
                               columns=modelcfg.categoricals)
        else:
            x = df[modelcfg.features]

        y = df[modelcfg.dependent]

        if modelcfg.dependent_encode:
            y = modelcfg.dependent_encoder.fit_transform(y)

        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=modelcfg.testsize, random_state=0)

        x_train = DatasetPreprocessing.transform_columns(
            modelcfg.imputer.fit_transform, x_train, modelcfg.non_categoricals)
        x_test = DatasetPreprocessing.transform_columns(
            modelcfg.imputer.transform, x_test, modelcfg.non_categoricals)

        if modelcfg.has_standard_scaled():
            if not modelcfg.standard_scaler_fitted:
                x_train = DatasetPreprocessing.transform_columns(
                    modelcfg.standard_scaler.fit_transform, x_train, modelcfg.standard_scaled)
                modelcfg.standard_scaler_fitted = True

            x_test = DatasetPreprocessing.transform_columns(
                modelcfg.standard_scaler.transform, x_test, modelcfg.standard_scaled)

        return modelcfg, x_train, x_test, y_train, y_test

    @staticmethod
    def prepare_prediction(modelcfg, df):
        if modelcfg.has_categoricals():
            x = pd.get_dummies(df[modelcfg.features],
                               columns=modelcfg.categoricals)
        else:
            x = df[modelcfg.features]

        x = x.reindex(columns=modelcfg.columns, fill_value=0)

        x = DatasetPreprocessing.transform_columns(
            modelcfg.imputer.transform, x, modelcfg.non_categoricals)

        if modelcfg.has_standard_scaled():
            x = DatasetPreprocessing.transform_columns(
                modelcfg.standard_scaler.transform, x, modelcfg.standard_scaled)

        return x

    @staticmethod
    def transform_columns(func, df, columns):
        df_temp = df.copy()
        df_temp[columns] = func(df[columns])
        return df_temp
