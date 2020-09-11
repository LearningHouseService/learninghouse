import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

class DatasetPreprocessing():
    @staticmethod
    def prepareTraining(modelcfg, df):
        if modelcfg.hasCategoricals():
            x = pd.get_dummies(df[modelcfg.features], columns=modelcfg.categoricals)
        else:
            x = df[modelcfg.features]
    
        y = df[modelcfg.dependent]

        if modelcfg.dependentEncode:
            le = LabelEncoder()
            y = le.fit_transform(y)

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = modelcfg.testsize, random_state = 0)

        x_train = DatasetPreprocessing.transformColumns(modelcfg.imputer.fit_transform, x_train, modelcfg.nonCategoricals)
        x_test = DatasetPreprocessing.transformColumns(modelcfg.imputer.transform, x_test, modelcfg.nonCategoricals)

        if modelcfg.hasStandardScaled():
            if not modelcfg.standard_scaler_fitted:
                x_train = DatasetPreprocessing.transformColumns(modelcfg.standard_scaler.fit_transform, x_train, modelcfg.standard_scaled)
                modelcfg.standard_scaler_fitted = True

            x_test = DatasetPreprocessing.transformColumns(modelcfg.standard_scaler.transform, x_test, modelcfg.standard_scaled)
                
        return modelcfg, x_train, x_test, y_train, y_test

    @staticmethod
    def preparePrediction(modelcfg, df):
        if modelcfg.hasCategoricals():
            x = pd.get_dummies(df[modelcfg.features], columns=modelcfg.categoricals)
        else:
            x = df[modelcfg.features]

        x = x.reindex(columns=modelcfg.columns, fill_value=0)
 
        x = DatasetPreprocessing.transformColumns(modelcfg.imputer.transform, x, modelcfg.nonCategoricals)

        if modelcfg.hasStandardScaled():
            x = DatasetPreprocessing.transformColumns(modelcfg.standard_scaler.transform, x, modelcfg.standard_scaled)

        return x

    @staticmethod
    def transformColumns(func, df, columns):
        df_temp = df.copy()
        df_temp[columns] = func(df[columns])
        return df_temp