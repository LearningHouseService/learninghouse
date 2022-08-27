import { Component } from '@angular/core';
import { MediaObserver } from '@angular/flex-layout';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/modules/auth/auth.service';
import { SidenavService } from '../sidenav/sidenav.service';
import { InfoDialogComponent } from '../info-dialog/info-dialog.component';

@Component({
  selector: 'app-toolbar',
  templateUrl: './toolbar.component.html',
  styleUrls: ['./toolbar.component.scss']
})
export class ToolbarComponent {

  constructor(
    public sidenavService: SidenavService,
    public authService: AuthService,
    public dialog: MatDialog,
    private router: Router,
    public media$: MediaObserver) { }

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
