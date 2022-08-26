import { Component } from '@angular/core';
import { AuthService } from 'src/app/modules/auth/auth.service';
import { APIService } from 'src/app/shared/services/api.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent {

  constructor(private api: APIService, public authService: AuthService) { }


  test() {
    this.api.get('/brain/darkness/info').subscribe();
  }

}
