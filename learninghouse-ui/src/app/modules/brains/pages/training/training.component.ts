import { Component } from '@angular/core';
import { AlertType } from 'src/app/shared/components/alert/alert.component';

@Component({
  selector: 'app-training',
  templateUrl: './training.component.html',
  styleUrls: ['./training.component.scss']
})
export class TrainingComponent {

  get AlertType() {
    return AlertType;
  }

}
