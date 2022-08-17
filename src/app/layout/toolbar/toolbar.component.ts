import { Component } from '@angular/core';
import { AuthService } from 'src/app/auth/auth.service';
import { LayoutService } from '../layout.service';

@Component({
  selector: 'app-toolbar',
  templateUrl: './toolbar.component.html',
  styleUrls: ['./toolbar.component.scss']
})
export class ToolbarComponent {

  constructor(public layoutService: LayoutService, public authService: AuthService) { }

}
