import { Component, Input } from '@angular/core';

export enum AlertType {
  success = 'success',
  error = 'error',
  warning = 'warning'
}

@Component({
  selector: 'learninghouse-alert',
  templateUrl: './alert.component.html',
  styleUrls: ['./alert.component.scss']
})
export class AlertComponent {
  @Input()
  alertType = AlertType.warning


}
