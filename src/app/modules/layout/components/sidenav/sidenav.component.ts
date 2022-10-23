import { Component, ViewEncapsulation } from '@angular/core';
import { MediaObserver } from '@angular/flex-layout';
import { Router } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { AuthService } from 'src/app/modules/auth/auth.service';
import { Role } from 'src/app/shared/models/auth.model';
import { SidenavService } from './sidenav.service';

export interface SidenavItem {
  key: string;
  minimumRole?: Role;
  icon?: string;
  svg?: string;
  route?: string;
  children?: SidenavItem[];
}

@Component({
  selector: 'app-sidenav',
  templateUrl: './sidenav.component.html',
  styleUrls: ['./sidenav.component.scss']
})
export class SidenavComponent {

  navItems: SidenavItem[] = [
    {
      key: 'dashboard',
      icon: 'dashboard',
      route: '/dashboard',
      minimumRole: Role.USER
    },
    {
      key: 'prediction',
      svg: 'learninghouse',
      route: '/brains/prediction',
      minimumRole: Role.USER
    },
    {
      key: 'training',
      icon: 'model_training',
      route: '/brains/training',
      minimumRole: Role.TRAINER
    },
    {
      key: 'configuration',
      icon: 'settings',
      minimumRole: Role.ADMIN,
      children: [
        {
          key: 'brains',
          svg: 'learninghouse',
          route: '/configuration/brains'
        },
        {
          key: 'sensors',
          icon: 'device_hub',
          route: '/configuration/sensors'
        },
        {
          key: 'apikeys',
          icon: 'key',
          route: '/auth/apikeys',
        },
        {
          key: 'password',
          icon: 'password',
          route: '/auth/change_password'
        }
      ]
    }
  ]

  constructor(public sidenavService: SidenavService,
    public authService: AuthService,
    public media$: MediaObserver,
    private router: Router,
    private translateService: TranslateService) { }

  logout() {
    this.authService.logout();
    this.router.navigate(['/auth']);
  }

}
