import { HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { JwtHelperService } from '@auth0/angular-jwt';
import { BehaviorSubject, catchError, map, Observable } from 'rxjs';
import { APIKeyModel, APIKeyRole, ChangePasswordRequestModel, LoginRequestModel, Role, TokenModel } from '../../shared/models/auth.model';
import { APIService } from '../../shared/services/api.service';


@Injectable({
  providedIn: 'root'
})
export class AuthService {
  role$ = new BehaviorSubject<Role | null>(null);
  refreshTokenExpireDate$ = new BehaviorSubject<Date | null>(null);

  private jwtService = new JwtHelperService();

  constructor(private api: APIService) {
  }

  loginAdmin(loginPayload: LoginRequestModel) {
    this.logout();
    return this.api
      .post<TokenModel>('/auth/token', loginPayload)
      .pipe(
        map((tokens) => this.handleTokens(tokens))
      )
  }

  changePassword(changePassword: ChangePasswordRequestModel) {
    return this.api.put<boolean>('/auth/password', changePassword);
  }

  restoreSession() {
    let tokens = this.getTokens();
    if (!tokens) {
      this.getAPIKey()
    }
  }

  getAccessToken(): string {
    let accessToken = '';
    const tokens = this.getTokens();
    if (tokens) {
      this.changeRole(Role.ADMIN);
      if (!this.jwtService.isTokenExpired(tokens?.access_token)) {
        accessToken = tokens.access_token;
      }
    }

    return accessToken;
  }

  loginAPIKey(apikey: string) {
    this.logout();
    sessionStorage.setItem('apikey', apikey);
    const headers = new HttpHeaders({
      'X-LEARNINGHOUSE-API-KEY': apikey
    })
    return this.api.get<string>('/auth/role', { headers: headers })
      .pipe(
        map((role) => {
          sessionStorage.setItem('apikey_role', role);
          this.changeRole(Role.fromString(role));
        }),
        catchError((error) => {
          sessionStorage.removeItem('apikey');
          sessionStorage.removeItem('apikey_role');
          throw error;
        })
      );
  }

  logout() {
    const tokens = this.getTokens();
    if (tokens) {
      sessionStorage.removeItem('tokens');
      const headers = new HttpHeaders({
        'Authorization': 'Bearer ' + tokens.refresh_token
      });
      this.api.delete<boolean>('/auth/token', { headers: headers })
        .subscribe();
    }

    if (this.getAPIKey()) {
      sessionStorage.removeItem('apikey');
      sessionStorage.removeItem('apikey_role');
    }

    this.unsetRole();
  }

  getAPIKey(): string {
    let apikey = sessionStorage.getItem('apikey');
    if (apikey) {
      let role = sessionStorage.getItem('apikey_role');
      if (role) {
        this.changeRole(Role.fromString(role));
      }
    } else {
      apikey = '';
      this.unsetRole();
    }

    return apikey;
  }

  isAPIKey(): boolean {
    return this.role$.getValue() === Role.TRAINER || this.role$.getValue() === Role.USER;
  }

  refreshToken(): Observable<TokenModel> | null {
    let request: Observable<TokenModel> | null = null;
    const tokens = this.getTokens();
    if (tokens) {
      if (!this.jwtService.isTokenExpired(tokens?.refresh_token)) {
        const headers = new HttpHeaders({
          'Authorization': 'Bearer ' + tokens.refresh_token
        });
        request = this.api.put<TokenModel>('/auth/token', null, { headers: headers })
          .pipe(
            map((new_tokens) => this.handleTokens(new_tokens))
          )
      }
    }

    return request
  }

  private handleTokens(tokens: TokenModel): TokenModel {
    sessionStorage.setItem('tokens', JSON.stringify(tokens));
    this.changeRole(Role.ADMIN)
    this.refreshTokenExpireDate$.next(this.jwtService.getTokenExpirationDate(tokens.refresh_token));

    return tokens;
  }

  getTokens(): TokenModel | null {
    let tokens = null;
    let sessionStorageTokens = sessionStorage.getItem('tokens');
    if (sessionStorageTokens) {
      tokens = JSON.parse(sessionStorageTokens) as TokenModel;
      if (this.jwtService.isTokenExpired(tokens?.refresh_token)) {
        tokens = null;
        sessionStorage.removeItem('tokens');
        this.unsetRole();
      } else {
        this.changeRole(Role.ADMIN);
        this.refreshTokenExpireDate$.next(this.jwtService.getTokenExpirationDate(tokens.refresh_token));
      }
    }
    return tokens
  }

  unsetRole(): void {
    this.changeRole(null);
  }

  private changeRole(role: Role | null): void {
    this.role$.next(role)
    if (!role) {
      this.refreshTokenExpireDate$.next(null);
    }
  }

  public getAPIKeys(): Observable<APIKeyModel[]> {
    return this.api.get<APIKeyModel[]>('/auth/apikeys')
  }

  public addAPIKey(apikey: APIKeyModel): Observable<APIKeyModel> {
    return this.api.post<APIKeyModel>('/auth/apikey', {
      description: apikey.description,
      role: APIKeyRole[apikey.role]
    });
  }

  public deleteAPIKey(description: string): Observable<string> {
    return this.api.delete('/auth/apikey/' + description);
  }

}