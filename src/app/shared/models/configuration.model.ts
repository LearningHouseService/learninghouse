export enum SensorType {
    NUMERICAL = 'numerical',
    CATEGORICAL = 'categorical'
}

export interface SensorModel {
    name: string;
    typed: SensorType;
}