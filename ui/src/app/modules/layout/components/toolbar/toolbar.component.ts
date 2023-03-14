import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/modules/auth/auth.service';
import { SidenavService } from '../sidenav/sidenav.service';
import { InfoDialogComponent } from '../info-dialog/info-dialog.component';
import { BreakpointService } from 'src/app/shared/services/breakpoint.service';

@Component({
  selector: 'app-toolbar',
  templateUrl: './toolbar.component.html'
})
export class ToolbarComponent {

  constructor(
    public sidenavService: SidenavService,
    public authService: AuthService,
    public breakpoints: BreakpointService,
    public dialog: MatDialog,
    private router: Router) { }

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

  openVersionsDialog() {
    this.dialog.open(InfoDialogComponent);
  }
}
