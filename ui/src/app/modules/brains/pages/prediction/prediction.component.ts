import { Component } from '@angular/core';
import { AlertType } from 'src/app/shared/components/alert/alert.component';

@Component({
  selector: 'app-prediction',
  templateUrl: './prediction.component.html'
})
export class PredictionComponent {

  get AlertType() {
    return AlertType;
  }

}
