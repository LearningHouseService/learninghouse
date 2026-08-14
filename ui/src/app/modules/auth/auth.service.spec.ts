import { Router } from '@angular/router';
import { of, throwError } from 'rxjs';
import { AuthService } from './auth.service';
import { APIKeyModel, APIKeyRole, ChangePasswordRequestModel, LoginRequestModel, Role, TokenModel } from './auth.model';
import { APIService } from '../../shared/services/api.service';

function makeToken(expiresInSeconds: number): string {
  const encode = (obj: object) => btoa(JSON.stringify(obj));
  const header = encode({ alg: 'HS256', typ: 'JWT' });
  const payload = encode({ sub: 'test', exp: Math.floor(Date.now() / 1000) + expiresInSeconds });
  return `${header}.${payload}.signature`;
}

function storeTokens(accessExpiresIn: number, refreshExpiresIn: number): TokenModel {
  const tokens: TokenModel = {
    access_token: makeToken(accessExpiresIn),
    refresh_token: makeToken(refreshExpiresIn),
    token_type: 'bearer'
  };
  sessionStorage.setItem('tokens', JSON.stringify(tokens));
  return tokens;
}

describe('AuthService', () => {
  let service: AuthService;
  let api: jasmine.SpyObj<APIService>;
  let router: jasmine.SpyObj<Router>;

  beforeEach(() => {
    sessionStorage.clear();
    api = jasmine.createSpyObj<APIService>('APIService', ['get', 'post', 'put', 'delete']);
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    service = new AuthService(api, router);
  });

  afterEach(() => {
    sessionStorage.clear();
  });

  describe('loginAdmin', () => {
    it('should store the returned tokens and switch the role to admin', () => {
      const tokens = { access_token: makeToken(600), refresh_token: makeToken(3600), token_type: 'bearer' };
      api.post.and.returnValue(of(tokens));
      const payload: LoginRequestModel = { password: 'secret' };

      service.loginAdmin(payload).subscribe();

      expect(api.post).toHaveBeenCalledWith('/auth/token', payload);
      expect(JSON.parse(sessionStorage.getItem('tokens')!)).toEqual(tokens);
      expect(service.role$.getValue()).toBe(Role.ADMIN);
      expect(service.refreshTokenExpireDate$.getValue()).toBeInstanceOf(Date);
    });

    it('should log out any previous session first', () => {
      storeTokens(600, 3600);
      api.delete.and.returnValue(of(true));
      api.post.and.returnValue(of({ access_token: makeToken(600), refresh_token: makeToken(3600), token_type: 'bearer' }));

      service.loginAdmin({ password: 'secret' }).subscribe();

      expect(api.delete).toHaveBeenCalled();
    });
  });

  describe('changePassword', () => {
    it('should delegate to the API without transforming the payload', () => {
      api.put.and.returnValue(of(true));
      const payload: ChangePasswordRequestModel = { old_password: 'old', new_password: 'new' };

      service.changePassword(payload).subscribe();

      expect(api.put).toHaveBeenCalledWith('/auth/password', payload);
    });
  });

  describe('getAccessToken', () => {
    it('should return empty and leave the role unset when there are no stored tokens', () => {
      expect(service.getAccessToken()).toBe('');
      expect(service.role$.getValue()).toBeNull();
    });

    it('should return the access token and switch to admin when both tokens are valid', () => {
      const tokens = storeTokens(600, 3600);

      expect(service.getAccessToken()).toBe(tokens.access_token);
      expect(service.role$.getValue()).toBe(Role.ADMIN);
    });

    it('should return empty but keep the admin role when only the access token expired', () => {
      storeTokens(-600, 3600);

      expect(service.getAccessToken()).toBe('');
      expect(service.role$.getValue()).toBe(Role.ADMIN);
    });

    it('should return empty and clear the role when the refresh token expired', () => {
      storeTokens(600, -3600);

      expect(service.getAccessToken()).toBe('');
      expect(service.role$.getValue()).toBeNull();
      expect(sessionStorage.getItem('tokens')).toBeNull();
    });
  });

  describe('refreshToken', () => {
    it('should return null when there are no stored tokens', () => {
      expect(service.refreshToken()).toBeNull();
    });

    it('should return null when the refresh token itself expired', () => {
      storeTokens(600, -3600);

      expect(service.refreshToken()).toBeNull();
    });

    it('should request new tokens and store them when the refresh token is valid', () => {
      storeTokens(-600, 3600);
      const newTokens = { access_token: makeToken(600), refresh_token: makeToken(3600), token_type: 'bearer' };
      api.put.and.returnValue(of(newTokens));

      const request = service.refreshToken();
      expect(request).not.toBeNull();

      request!.subscribe((result) => {
        expect(result).toEqual(newTokens);
      });

      expect(api.put).toHaveBeenCalledWith('/auth/token', null, jasmine.objectContaining({ headers: jasmine.anything() }));
      expect(JSON.parse(sessionStorage.getItem('tokens')!)).toEqual(newTokens);
    });
  });

  describe('loginAPIKey', () => {
    it('should store the API key and derive the trainer role', () => {
      api.get.and.returnValue(of('trainer'));

      service.loginAPIKey('the-key').subscribe();

      expect(sessionStorage.getItem('apikey')).toBe('the-key');
      expect(sessionStorage.getItem('apikey_role')).toBe('trainer');
      expect(service.role$.getValue()).toBe(Role.TRAINER);
    });

    it('should store the API key and derive the user role', () => {
      api.get.and.returnValue(of('user'));

      service.loginAPIKey('the-key').subscribe();

      expect(service.role$.getValue()).toBe(Role.USER);
    });

    it('should not derive the admin role from the string "admin" (known bug in Role.fromString)', () => {
      // Role.fromString compares its uninitialized local variable instead of the
      // input string in the admin branch, so it is unreachable today. Characterizing
      // the current behaviour here rather than silently relying on a fix.
      api.get.and.returnValue(of('admin'));

      service.loginAPIKey('the-key').subscribe();

      expect(service.role$.getValue()).toBeNull();
    });

    it('should clear the stored API key when the role lookup fails', () => {
      api.get.and.returnValue(throwError(() => new Error('unauthorized')));

      service.loginAPIKey('the-key').subscribe({ error: () => undefined });

      expect(sessionStorage.getItem('apikey')).toBeNull();
      expect(sessionStorage.getItem('apikey_role')).toBeNull();
    });
  });

  describe('getAPIKey', () => {
    it('should return empty and unset the role when nothing is stored', () => {
      service.role$.next(Role.TRAINER);

      expect(service.getAPIKey()).toBe('');
      expect(service.role$.getValue()).toBeNull();
    });

    it('should return the stored key and restore its role', () => {
      sessionStorage.setItem('apikey', 'the-key');
      sessionStorage.setItem('apikey_role', 'user');

      expect(service.getAPIKey()).toBe('the-key');
      expect(service.role$.getValue()).toBe(Role.USER);
    });
  });

  describe('isAPIKey', () => {
    it('should be true for trainer and user roles, false otherwise', () => {
      service.role$.next(Role.TRAINER);
      expect(service.isAPIKey()).toBeTrue();

      service.role$.next(Role.USER);
      expect(service.isAPIKey()).toBeTrue();

      service.role$.next(Role.ADMIN);
      expect(service.isAPIKey()).toBeFalse();

      service.role$.next(null);
      expect(service.isAPIKey()).toBeFalse();
    });
  });

  describe('logout', () => {
    it('should clear a stored token session and unset the role', () => {
      storeTokens(600, 3600);
      api.delete.and.returnValue(of(true));

      service.logout();

      expect(sessionStorage.getItem('tokens')).toBeNull();
      expect(api.delete).toHaveBeenCalledWith('/auth/token', jasmine.objectContaining({ headers: jasmine.anything() }));
      expect(service.role$.getValue()).toBeNull();
    });

    it('should clear a stored API key session and unset the role', () => {
      sessionStorage.setItem('apikey', 'the-key');
      sessionStorage.setItem('apikey_role', 'user');

      service.logout();

      expect(sessionStorage.getItem('apikey')).toBeNull();
      expect(sessionStorage.getItem('apikey_role')).toBeNull();
      expect(service.role$.getValue()).toBeNull();
    });

    it('should be a no-op beyond unsetting the role when nothing is stored', () => {
      service.logout();

      expect(api.delete).not.toHaveBeenCalled();
      expect(service.role$.getValue()).toBeNull();
    });
  });

  describe('restoreSession', () => {
    it('should restore the admin role from stored tokens', () => {
      storeTokens(600, 3600);

      service.restoreSession();

      expect(service.role$.getValue()).toBe(Role.ADMIN);
    });

    it('should fall back to the stored API key when there are no tokens', () => {
      sessionStorage.setItem('apikey', 'the-key');
      sessionStorage.setItem('apikey_role', 'trainer');

      service.restoreSession();

      expect(service.role$.getValue()).toBe(Role.TRAINER);
    });
  });

  describe('API key management', () => {
    it('should list API keys via the API', () => {
      const keys: APIKeyModel[] = [{ description: 'ci', role: APIKeyRole.USER }];
      api.get.and.returnValue(of(keys));

      service.getAPIKeys().subscribe((result) => {
        expect(result).toBe(keys);
      });

      expect(api.get).toHaveBeenCalledWith('/auth/apikeys');
    });

    it('should add an API key, forwarding only description and role', () => {
      const created: APIKeyModel = { description: 'ci', role: APIKeyRole.TRAINER, key: 'generated' };
      api.post.and.returnValue(of(created));

      service.addAPIKey({ description: 'ci', role: APIKeyRole.TRAINER, key: 'ignored-on-request' }).subscribe();

      expect(api.post).toHaveBeenCalledWith('/auth/apikey', { description: 'ci', role: APIKeyRole.TRAINER });
    });

    it('should delete an API key by description', () => {
      api.delete.and.returnValue(of('ci'));

      service.deleteAPIKey('ci').subscribe();

      expect(api.delete).toHaveBeenCalledWith('/auth/apikey/ci');
    });
  });
});
