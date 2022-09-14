import { Component, Input } from '@angular/core';
import { AlertType } from '../alert/alert.component';

@Component({
  selector: 'learninghouse-form-response',
  templateUrl: './form-response.component.html',
  styleUrls: ['./form-response.component.scss']
})
export class FormResponseComponent {
  public AlertType = AlertType

  @Input()
  success: boolean | null = false;

  @Input()
  successMessage: string = 'components.formresponse.success';

  @Input()
  error: string | null = null;

  @Input()
  errorPrefix: string = 'common.errors';
}
