import { HttpHandler, HttpRequest } from '@angular/common/http';
import { Router } from '@angular/router';
import { of, throwError } from 'rxjs';
import { AuthInterceptor } from './auth.interceptor';
import { AuthService } from '../../modules/auth/auth.service';
import { Role, TokenModel } from '../../modules/auth/auth.model';

describe('AuthInterceptor', () => {
  let interceptor: AuthInterceptor;
  let authService: jasmine.SpyObj<Pick<AuthService, 'getAccessToken' | 'getAPIKey' | 'refreshToken' | 'logout'>> & { role$: { getValue: () => Role | null } };
  let router: jasmine.SpyObj<Router>;
  let handler: jasmine.SpyObj<HttpHandler>;
  let currentRole: Role | null;

  beforeEach(() => {
    currentRole = null;
    authService = {
      ...jasmine.createSpyObj('AuthService', ['getAccessToken', 'getAPIKey', 'refreshToken', 'logout']),
      role$: { getValue: () => currentRole }
    };
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    handler = jasmine.createSpyObj<HttpHandler>('HttpHandler', ['handle']);
    handler.handle.and.returnValue(of({} as any));

    interceptor = new AuthInterceptor(authService as unknown as AuthService, router);
  });

  function forwardedRequest(): HttpRequest<any> {
    return handler.handle.calls.mostRecent().args[0] as HttpRequest<any>;
  }

  it('should pass /auth/token through unchanged regardless of role', () => {
    currentRole = Role.ADMIN;
    authService.getAccessToken.and.returnValue('access-token');
    const request = new HttpRequest('POST', 'http://localhost:5000/api/auth/token', {});

    interceptor.intercept(request, handler).subscribe();

    expect(forwardedRequest()).toBe(request);
    expect(authService.getAccessToken).not.toHaveBeenCalled();
  });

  it('should pass /mode and /versions through unchanged', () => {
    const modeRequest = new HttpRequest('GET', 'http://localhost:5000/api/mode');
    interceptor.intercept(modeRequest, handler).subscribe();
    expect(forwardedRequest()).toBe(modeRequest);

    const versionsRequest = new HttpRequest('GET', 'http://localhost:5000/api/versions');
    interceptor.intercept(versionsRequest, handler).subscribe();
    expect(forwardedRequest()).toBe(versionsRequest);
  });

  it('should attach the access token as a Bearer header for an admin role', () => {
    currentRole = Role.ADMIN;
    authService.getAccessToken.and.returnValue('access-token');
    const request = new HttpRequest('GET', 'http://localhost:5000/api/brains/info');

    interceptor.intercept(request, handler).subscribe();

    expect(forwardedRequest().headers.get('Authorization')).toBe('Bearer access-token');
  });

  it('should refresh the token and attach it when no access token is available', () => {
    currentRole = Role.ADMIN;
    authService.getAccessToken.and.returnValue('');
    const newTokens: TokenModel = { access_token: 'new-access', refresh_token: 'new-refresh', token_type: 'bearer' };
    authService.refreshToken.and.returnValue(of(newTokens));
    const request = new HttpRequest('GET', 'http://localhost:5000/api/brains/info');

    interceptor.intercept(request, handler).subscribe();

    expect(forwardedRequest().headers.get('Authorization')).toBe('Bearer new-access');
    expect(authService.logout).not.toHaveBeenCalled();
  });

  it('should log out and redirect to /auth when the refresh request fails', () => {
    currentRole = Role.ADMIN;
    authService.getAccessToken.and.returnValue('');
    authService.refreshToken.and.returnValue(throwError(() => new Error('refresh failed')));
    const request = new HttpRequest('GET', 'http://localhost:5000/api/brains/info');

    interceptor.intercept(request, handler).subscribe({
      error: () => {
        // expected: the interceptor rethrows after logging out
      }
    });

    expect(authService.logout).toHaveBeenCalled();
    expect(router.navigate).toHaveBeenCalledWith(['/auth']);
  });

  it('should log out and redirect to /auth when there is no access token and refreshToken() is unavailable', () => {
    currentRole = Role.ADMIN;
    authService.getAccessToken.and.returnValue('');
    authService.refreshToken.and.returnValue(null);
    const request = new HttpRequest('GET', 'http://localhost:5000/api/brains/info');

    interceptor.intercept(request, handler).subscribe();

    expect(authService.logout).toHaveBeenCalled();
    expect(router.navigate).toHaveBeenCalledWith(['/auth']);
    expect(forwardedRequest()).toBe(request);
  });

  it('should attach the API key header for a trainer role', () => {
    currentRole = Role.TRAINER;
    authService.getAPIKey.and.returnValue('the-api-key');
    const request = new HttpRequest('GET', 'http://localhost:5000/api/brains/info');

    interceptor.intercept(request, handler).subscribe();

    expect(forwardedRequest().headers.get('X-LEARNINGHOUSE-API-KEY')).toBe('the-api-key');
  });

  it('should attach the API key header for a user role', () => {
    currentRole = Role.USER;
    authService.getAPIKey.and.returnValue('the-api-key');
    const request = new HttpRequest('GET', 'http://localhost:5000/api/brains/info');

    interceptor.intercept(request, handler).subscribe();

    expect(forwardedRequest().headers.get('X-LEARNINGHOUSE-API-KEY')).toBe('the-api-key');
  });

  it('should pass the request through unchanged for an API-key role with no stored key', () => {
    currentRole = Role.USER;
    authService.getAPIKey.and.returnValue('');
    const request = new HttpRequest('GET', 'http://localhost:5000/api/brains/info');

    interceptor.intercept(request, handler).subscribe();

    expect(forwardedRequest()).toBe(request);
  });

  it('should pass the request through unchanged when there is no role at all', () => {
    currentRole = null;
    const request = new HttpRequest('GET', 'http://localhost:5000/api/brains/info');

    interceptor.intercept(request, handler).subscribe();

    expect(forwardedRequest()).toBe(request);
    expect(authService.getAccessToken).not.toHaveBeenCalled();
    expect(authService.getAPIKey).not.toHaveBeenCalled();
  });
});
