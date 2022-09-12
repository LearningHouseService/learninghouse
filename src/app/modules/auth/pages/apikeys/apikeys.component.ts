import { Component } from '@angular/core';
import { AlertType } from 'src/app/shared/components/alert/alert.component';

@Component({
  selector: 'app-apikeys',
  templateUrl: './apikeys.component.html',
  styleUrls: ['./apikeys.component.scss']
})
export class APIKeysComponent {

  get AlertType() {
    return AlertType;
  }

}
