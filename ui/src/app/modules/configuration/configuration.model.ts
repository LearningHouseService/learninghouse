export enum SensorType {
    NUMERICAL = 'numerical',
    CATEGORICAL = 'categorical',
    CYCLICAL = 'cyclical',
    TIME = 'time'
}

export interface SensorConfigurationModel {
    name: string;
    typed: SensorType;
    cycles: number;
    calc_sun_position: boolean;
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