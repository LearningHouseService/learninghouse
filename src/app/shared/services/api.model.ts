export enum ServiceMode {
    INITIAL = 'initial',
    DEVELOPMENT = 'development',
    PRODUCTION = 'production'
}

export interface LearningHouseErrorMessage {
    error: string;
    description: string;
}