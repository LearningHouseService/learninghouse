import {
  HttpEvent, HttpHandler, HttpInterceptor, HttpRequest
} from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, Observable, switchMap } from 'rxjs';
import { AuthService } from '../../modules/auth/auth.service';
import { Role, TokenModel } from '../../modules/auth/auth.model';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {

  unprotected_endpoints = [
    '/auth/token',
    '/mode',
    '/versions'
  ]

  constructor(private authService: AuthService, private router: Router) { }

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (!this.isUnprotectedEndpoint(request.url)) {
      const role = this.authService.role$.getValue();
      if (role === Role.ADMIN) {
        let requestWithAccessToken = this.handleAccessToken(request, next);
        if (requestWithAccessToken) {
          return requestWithAccessToken;
        }
      } else if (role === Role.TRAINER || role === Role.USER) {
        let apikey = this.authService.getAPIKey();
        if (apikey) {
          return next.handle(request.clone({
            headers: request.headers.set('X-LEARNINGHOUSE-API-KEY', apikey)
          }));
        }
      }
    }

    return next.handle(request);
  }

  private isUnprotectedEndpoint(url: string): boolean {
    let unprotected_endpoint = false;
    for (const endpoint of this.unprotected_endpoints) {
      if (url.endsWith(endpoint)) {
        unprotected_endpoint = true;
        break;
      }
    }

    return unprotected_endpoint;
  }

  private handleAccessToken(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> | null {
    let accessToken = this.authService.getAccessToken();
    if (accessToken) {
      return next.handle(request.clone({
        headers: request.headers.set('Authorization', 'Bearer ' + accessToken)
      }));
    } else {
      let refreshRequest = this.authService.refreshToken();
      if (refreshRequest) {
        return refreshRequest.pipe(
          switchMap((tokens: TokenModel) => {
            return next.handle(request.clone({
              headers: request.headers.set('Authorization', 'Bearer ' + tokens.access_token)
            }))
          }),
          catchError((error) => {
            this.authService.logout();
            this.router.navigate(['/auth']);
            throw error;
          })
        );
      }
    }

    return null;
  }
}
