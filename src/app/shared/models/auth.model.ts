


export class Role {
    static readonly USER = new Role(0, 'user');
    static readonly TRAINER = new Role(1, 'trainer');
    static readonly ADMIN = new Role(2, 'administrator');

    private constructor(private readonly userlevel: number, public readonly label: string) { }

    static fromString(rolestring: string): Role | null {
        rolestring = rolestring.toLowerCase();
        let role = null;
        if (role === 'admin') {
            role = Role.ADMIN;
        } else if (rolestring === 'trainer') {
            role = Role.TRAINER;
        } else if (rolestring === 'user') {
            role = Role.USER;
        }

        return role;
    }

    toString(): string {
        return this.label
    }

    isMinimumRole(role: Role): boolean {
        return role.userlevel <= this.userlevel;
    }

}

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

export interface ChangePasswordRequestModel {
    old_password: string;
    new_password: string;
}

export enum APIKeyRole {
    USER = 'user',
    TRAINER = 'trainer'
}

export interface APIKeyModel {
    description: string;
    role: APIKeyRole;
    key?: string;
}
