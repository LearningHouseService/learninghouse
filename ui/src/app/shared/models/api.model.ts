export enum ServiceMode {
    INITIAL = 'initial',
    DEVELOPMENT = 'development',
    PRODUCTION = 'production',
    UNKNOWN = 'unknown'
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
export interface LearningHouseVersions {
    service: string;
    fastapi: string;
    pydantic: string;
    uvicorn: string;
    sklearn: string;
    numpy: string;
    pandas: string;
    jwt: string;
    passlib: string;
    loguru: string;
}


export interface VersionItem {
    label: string;
    version: string;
}