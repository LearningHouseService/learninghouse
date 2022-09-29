import { Component, Input } from '@angular/core';
import { AlertType } from '../alert/alert.component';

export interface FormResponseConfig {
  successMessage?: string;
  errorPrefix?: string;
}
@Component({
  selector: 'learninghouse-form-response',
  templateUrl: './form-response.component.html',
  styleUrls: ['./form-response.component.scss']
})
export class FormResponseComponent {
  public AlertType = AlertType

  @Input()
  set config(values: FormResponseConfig) {
    this._config = {
      successMessage: 'common.messages.success',
      errorPrefix: 'common.errors',
      ...values
    };
  }

  get config(): FormResponseConfig {
    return this._config;
  }

  private _config = {}

  @Input()
  state?: string | null = null;
}
