import { Injectable } from '@angular/core';
import { APIService } from '../shared/services/api.service';
import { JwtHelperService } from '@auth0/angular-jwt';
import { BehaviorSubject, catchError, map, of } from 'rxjs';
import { LoginRequestModel, TokenModel, TokenPayloadModel } from './auth.model';


@Injectable({
  providedIn: 'root'
})
export class AuthService {

  access_token = new BehaviorSubject<TokenPayloadModel | null>(null);

  constructor(private api: APIService, private jwtService: JwtHelperService) { }

  login(loginPayload: LoginRequestModel) {
    return this.api
      .post('/auth/token', loginPayload)
      .pipe(
        map((data) => {
          const tokens = data as TokenModel;
          sessionStorage.setItem('tokens', JSON.stringify(tokens))

          const tokenPayload = this.jwtService.decodeToken(
            tokens.access_token
          );

          this.access_token.next(tokenPayload);

          return true;
        }),
        catchError((error) => {
          console.log(error);
          return of(false);
        })
      )
  }
}

