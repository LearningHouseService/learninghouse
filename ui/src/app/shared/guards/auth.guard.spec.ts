import { Router, UrlTree } from '@angular/router';
import { BehaviorSubject, Observable } from 'rxjs';
import { AuthGuard } from './auth.guard';
import { AuthService } from '../../modules/auth/auth.service';
import { Role } from '../../modules/auth/auth.model';

describe('AuthGuard', () => {
  let guard: AuthGuard;
  let authService: { role$: BehaviorSubject<Role | null> };
  let router: jasmine.SpyObj<Router>;
  let urlTree: UrlTree;

  beforeEach(() => {
    authService = { role$: new BehaviorSubject<Role | null>(null) };
    urlTree = {} as UrlTree;
    router = jasmine.createSpyObj<Router>('Router', ['createUrlTree']);
    router.createUrlTree.and.returnValue(urlTree);

    guard = new AuthGuard(authService as unknown as AuthService, router);
  });

  function check(minimumRole: Role): Observable<boolean | UrlTree> {
    return guard.checkMinimumRole(minimumRole) as Observable<boolean | UrlTree>;
  }

  it('should allow navigation when the current role meets the minimum role needed', (done) => {
    authService.role$.next(Role.ADMIN);

    check(Role.USER).subscribe((result) => {
      expect(result).toBeTrue();
      expect(router.createUrlTree).not.toHaveBeenCalled();
      done();
    });
  });

  it('should redirect to /brains when the current role is below the minimum role needed', (done) => {
    authService.role$.next(Role.USER);

    check(Role.ADMIN).subscribe((result) => {
      expect(result).toBe(urlTree);
      expect(router.createUrlTree).toHaveBeenCalledWith(['/brains']);
      done();
    });
  });

  it('should redirect to /auth when there is no role at all', (done) => {
    authService.role$.next(null);

    check(Role.USER).subscribe((result) => {
      expect(result).toBe(urlTree);
      expect(router.createUrlTree).toHaveBeenCalledWith(['/auth']);
      done();
    });
  });
});
