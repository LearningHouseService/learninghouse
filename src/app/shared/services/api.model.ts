export enum ServiceMode {
    INITIAL = 'initial',
    DEVELOPMENT = 'development',
    PRODUCTION = 'production'
}

export interface LearningHouseErrorMessage {
    error: string;
    description: string;
}

export class LearningHouseError extends Error {
    constructor(public status: number, public key: string, public override message: string) {
        super(message);
    }
}