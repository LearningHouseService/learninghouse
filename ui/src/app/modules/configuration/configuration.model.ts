export enum SensorType {
    NUMERICAL = 'numerical',
    CATEGORICAL = 'categorical'
}

export interface SensorConfigurationModel {
    name: string;
    typed: SensorType;
}

export enum BrainEstimatorType {
    CLASSIFIER = 'classifier',
    REGRESSOR = 'regressor'
}

export interface BrainEstimatorConfigurationModel {
    typed: BrainEstimatorType;
    estimators?: number;
    max_depth?: number;
    random_state?: number;
}

export interface BrainConfigurationModel {
    name: string;
    estimator: BrainEstimatorConfigurationModel;
    dependent_encode?: boolean;
    test_size: number;
}