import { Component, Input } from '@angular/core';

export class AlertType {
  static readonly success = new AlertType('success', 'check');

  static readonly error = new AlertType('error', 'error');

  static readonly warning = new AlertType('warning', 'warning');

  private constructor(public readonly css_class: string, public readonly icon: string) { }

  public toString(): string {
    return this.css_class
  }
}

@Component({
  selector: 'learninghouse-alert',
  templateUrl: './alert.component.html',
  styleUrls: ['./alert.component.scss']
})
export class AlertComponent {
  @Input()
  alertType = AlertType.warning;

}
