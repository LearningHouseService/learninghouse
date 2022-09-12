import { Component } from '@angular/core';
import { AlertType } from 'src/app/shared/components/alert/alert.component';

@Component({
  selector: 'app-brains',
  templateUrl: './brains.component.html',
  styleUrls: ['./brains.component.scss']
})
export class BrainsComponent {

  get AlertType() {
    return AlertType;
  }

}
