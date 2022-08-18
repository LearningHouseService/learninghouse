import { Component } from '@angular/core';
import { Role } from 'src/app/auth/auth.model';
import { AuthService } from 'src/app/auth/auth.service';
import { LayoutService } from '../layout.service';

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

  constructor(public layoutService: LayoutService, public authService: AuthService) { }

}
