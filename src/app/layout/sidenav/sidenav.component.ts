import { Component } from '@angular/core';
import { LayoutService } from '../layout.service';

export interface SiteNavItem {
  icon?: string;
  svg?: string;
  title: string;
  subtitle: string;
  minimum_role: string;
}

@Component({
  selector: 'app-sidenav',
  templateUrl: './sidenav.component.html',
  styleUrls: ['./sidenav.component.scss']
})
export class SidenavComponent {

  navItems: SiteNavItem[] = [
    { icon: 'dashboard', title: 'Dashboard', subtitle: 'Get a overview', minimum_role: 'user' },
    { svg: 'learninghouse', title: 'Prediction', subtitle: 'Use a brain', minimum_role: 'user' },
    { icon: 'model_training', title: 'Training', subtitle: 'Train a brain', minimum_role: 'trainer' },
    { icon: 'settings', title: 'Configuration', subtitle: 'Configure the service', minimum_role: 'admin' }
  ]

  constructor(public layoutService: LayoutService) { }

}
