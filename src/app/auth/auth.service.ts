import { Injectable } from '@angular/core';
import { APIService } from '../shared/services/api.service';
import { JwtHelperService } from '@auth0/angular-jwt';
import { BehaviorSubject, catchError, map, Observable, of } from 'rxjs';
import { LoginRequestModel, TokenModel, TokenPayloadModel } from './auth.model';
import { HttpHeaders } from '@angular/common/http';


@Injectable({
  providedIn: 'root'
})
export class AuthService {
  role$ = new BehaviorSubject<string | null>(null);
  user$ = new BehaviorSubject<boolean>(false);
  trainer$ = new BehaviorSubject<boolean>(false);
  admin$ = new BehaviorSubject<boolean>(false);

  private jwtService = new JwtHelperService();

  constructor(private api: APIService) {
    this.role$.subscribe((role) => {
      this.user$.next(role !== null);
      this.trainer$.next(role === 'admin' || role === 'trainer');
      this.admin$.next(role === 'admin');
    })
  }

  loginAdmin(loginPayload: LoginRequestModel) {
    this.logout();
    return this.api
      .post<TokenModel>('/auth/token', loginPayload)
      .pipe(
        map((tokens) => this.handleTokens(tokens))
      )
  }

  getAccessToken(): string {
    let accessToken = '';
    const tokens = this.getTokens();
    if (tokens) {
      this.role$.next('admin');
      if (!this.jwtService.isTokenExpired(tokens?.access_token)) {
        accessToken = tokens.access_token;
      }
    }

    return accessToken;
  }

  isAdmin(): boolean {
    this.getTokens();
    return this.role$.getValue() === 'admin';
  }

  isTrainer(): boolean {
    return this.isAdmin() || this.role$.getValue() === 'trainer';
  }

  isUser(): boolean {
    return this.isTrainer() || this.role$.getValue() === 'user';
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
          this.role$.next(role);
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

    this.role$.next(null);
  }

  getAPIKey(): string {
    let apikey = sessionStorage.getItem('apikey');
    if (apikey) {
      this.role$.next(sessionStorage.getItem('apikey_role'));
    } else {
      apikey = '';
      this.role$.next(null);
    }

    return apikey;
  }

  isAPIKey(): boolean {
    return this.role$.getValue() === 'trainer' || this.role$.getValue() === 'user';
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
    this.role$.next('admin')

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
        this.role$.next(null);
      } else {
        this.role$.next('admin');
      }
    }
    return tokens
  }

}

