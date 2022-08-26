import { Component } from '@angular/core';
import { MediaObserver } from '@angular/flex-layout';
import { Router } from '@angular/router';
import { Role } from 'src/app/shared/models/auth.model';
import { AuthService } from 'src/app/modules/auth/auth.service';
import { SidenavService } from './sidenav.service';

export interface SiteNavItem {
  icon?: string;
  svg?: string;
  title: string;
  subtitle: string;
  route: string;
  minimumRole: Role;
}

@Component({
  selector: 'app-sidenav',
  templateUrl: './sidenav.component.html',
  styleUrls: ['./sidenav.component.scss']
})
export class SidenavComponent {

  navItems: SiteNavItem[] = [
    {
      icon: 'dashboard',
      title: 'Dashboard',
      subtitle: 'Get a overview',
      route: '/dashboard',
      minimumRole: Role.USER
    },
    {
      svg: 'learninghouse',
      title: 'Prediction',
      subtitle: 'Use a brain',
      route: '/brains/prediction',
      minimumRole: Role.USER
    },
    {
      icon: 'model_training',
      title: 'Training',
      subtitle: 'Train a brain',
      route: '/brains/training',
      minimumRole: Role.TRAINER
    },
    {
      icon: 'settings',
      title: 'Configuration',
      subtitle: 'Configure the service',
      route: '/configuration',
      minimumRole: Role.ADMIN
    }
  ]

  constructor(public sidenavService: SidenavService, public authService: AuthService, private router: Router, public media$: MediaObserver) { }

  logout() {
    this.authService.logout();
    this.router.navigate(['/auth']);
  }

}
