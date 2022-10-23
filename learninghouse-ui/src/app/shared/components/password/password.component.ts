import { Component } from '@angular/core';
import { InputDirective } from '../input/input.directive';

@Component({
  selector: 'learninghouse-password',
  templateUrl: './password.component.html',
  styleUrls: ['./password.component.scss']
})
export class PasswordComponent extends InputDirective {
  hide = true;

}
