import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/auth/auth.service';
import { LayoutService } from '../layout.service';

@Component({
  selector: 'app-toolbar',
  templateUrl: './toolbar.component.html',
  styleUrls: ['./toolbar.component.scss']
})
export class ToolbarComponent {

  constructor(public layoutService: LayoutService, public authService: AuthService, private router: Router) { }

  logout() {
    this.authService.logout();
    this.router.navigate(['/auth']);
  }

  refresh() {
    let refresh_request = this.authService.refreshToken();
    if (refresh_request) {
      refresh_request.subscribe();
    } else {
      this.logout();
    }
  }
}
