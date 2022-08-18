import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { map, Observable, take } from 'rxjs';
import { Role } from './auth.model';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) { }

  canActivate(
    route: ActivatedRouteSnapshot,
    _: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    return this.authService.role$.pipe(
      take(1),
      map((role) => {
        if (role) {
          const minimumRole = route.data['minimumRole'] as Role;
          if (role.isMinimumRole(minimumRole)) {
            return true;
          } else {
            return this.router.createUrlTree(['/dashboard']);
          }
        } else {
          return this.router.createUrlTree(['/auth']);
        }
      })
    )
  }

}
