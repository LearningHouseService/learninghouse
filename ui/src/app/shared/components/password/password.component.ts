import { Component } from '@angular/core';
import { InputDirective } from '../input/input.directive';

@Component({
  selector: 'learninghouse-password',
  templateUrl: './password.component.html'
})
export class PasswordComponent extends InputDirective {
  hide = true;

}
