export enum SensorType {
    numerical,
    categorical
}

export interface Sensor {
    name: string;
    typed: SensorType;
}