import { Component } from '@angular/core';
import { InputDirective } from '../input/input.directive';

@Component({
  selector: 'learninghouse-password',
  standalone: false,
  templateUrl: './password.component.html'
})
export class PasswordComponent extends InputDirective {
  hide = true;

}
