import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor
} from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {

  unprotected_endpoints = [
    '/auth/token',
    '/mode',
    '/version'
  ]

  constructor(private authService: AuthService) { }

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    for (const element of this.unprotected_endpoints) {
      if (request.url.endsWith(element)) {
        console.log('Protected url');
        return next.handle(request);
      }
    }

    if (this.authService.isAdmin()) {
      let accessToken = this.authService.getAccessToken();
      if (accessToken) {
        let modifiedRequest = request.clone({
          headers: request.headers.set('Authorization', 'Bearer ' + accessToken)
        });
        return next.handle(modifiedRequest);
      }
    }

    return next.handle(request);
  }
}
