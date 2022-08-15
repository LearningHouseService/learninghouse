import { Component, Input } from '@angular/core';
import { FormFieldDirective } from '../formfield.directive';

@Component({
  selector: 'learninghouse-input',
  templateUrl: './input.component.html',
  styleUrls: ['./input.component.scss']
})
export class InputComponent extends FormFieldDirective {
  type = 'text';
}
