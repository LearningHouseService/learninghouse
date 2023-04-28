import { Injectable } from '@angular/core';
import { Router, UrlTree } from '@angular/router';
import { Observable, map, take } from 'rxjs';
import { AuthService } from '../../modules/auth/auth.service';
import { Role } from '../models/auth.model';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard {
  constructor(private authService: AuthService, private router: Router) { }

  checkMinimumRole(minimumRoleNeeded: Role): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    return this.authService.role$.pipe(
      take(1),
      map((role) => {
        if (role) {
          if (role.isMinimumRole(minimumRoleNeeded)) {
            return true;
          } else {
            return this.router.createUrlTree(['/brains/prediction']);
          }
        } else {
          return this.router.createUrlTree(['/auth']);
        }
      })
    )
  }

}
