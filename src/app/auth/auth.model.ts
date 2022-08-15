

export interface TokenModel {
    access_token: string;
    refresh_token: string;
    token_type: string;
}

export interface TokenPayloadModel {
    sub: string;
    iss: string;
    aud: string;
    jti: string;
    exp: number;
    iat: number;
}

export interface LoginRequestModel {
    password: string;
}
