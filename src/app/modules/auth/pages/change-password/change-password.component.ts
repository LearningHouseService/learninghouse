import { Component } from '@angular/core';
import { AlertType } from 'src/app/shared/components/alert/alert.component';

@Component({
  selector: 'app-change-password',
  templateUrl: './change-password.component.html',
  styleUrls: ['./change-password.component.scss']
})
export class ChangePasswordComponent {

  get AlertType() {
    return AlertType;
  }

}
