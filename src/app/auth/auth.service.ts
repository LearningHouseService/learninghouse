import { Injectable } from '@angular/core';
import { APIService } from '../shared/services/api.service';
import { JwtHelperService } from '@auth0/angular-jwt';
import { BehaviorSubject, catchError, map, of } from 'rxjs';
import { LoginRequestModel, TokenModel, TokenPayloadModel } from './auth.model';


@Injectable({
  providedIn: 'root'
})
export class AuthService {

  access_token$ = new BehaviorSubject<TokenPayloadModel | null>(null);
  role$ = new BehaviorSubject<string | null>(null);

  private jwtService = new JwtHelperService();

  constructor(private api: APIService) { }

  loginAdmin(loginPayload: LoginRequestModel) {
    return this.api
      .post<TokenModel>('/auth/token', loginPayload)
      .pipe(
        map((tokens) => {
          sessionStorage.setItem('tokens', JSON.stringify(tokens))

          const tokenPayload = this.jwtService.decodeToken(
            tokens.access_token
          );

          this.access_token$.next(tokenPayload);
          this.role$.next('admin')

          return true;
        })
      )
  }

  getAccessToken(): string {
    let accessToken = '';
    let sessionStorageTokens = sessionStorage.getItem('tokens');
    if (sessionStorageTokens) {
      let tokens = JSON.parse(sessionStorageTokens) as TokenModel;
      let isTokenExpired = this.jwtService.isTokenExpired(tokens?.access_token);
      if (isTokenExpired) {
        this.access_token$.next(null);
        this.role$.next(null);
      } else {
        const tokenPayload = this.jwtService.decodeToken(
          tokens.access_token
        );
        this.access_token$.next(tokenPayload);
        this.role$.next('admin');
        accessToken = tokens.access_token;
      }
    }

    return accessToken;
  }

  isAdmin(): boolean {
    return this.role$.getValue() === 'admin';
  }

}

