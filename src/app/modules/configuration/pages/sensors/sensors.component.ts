import { Component } from '@angular/core';
import { AlertType } from 'src/app/shared/components/alert/alert.component';

@Component({
  selector: 'app-sensors',
  templateUrl: './sensors.component.html',
  styleUrls: ['./sensors.component.scss']
})
export class SensorsComponent {

  get AlertType() {
    return AlertType;
  }

}
