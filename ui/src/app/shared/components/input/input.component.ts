import { Component, Input } from '@angular/core';
import { InputDirective } from './input.directive';

@Component({
  selector: 'learninghouse-input',
  standalone: false,
  templateUrl: './input.component.html',
  styleUrls: ['./input.component.scss']
})
export class InputComponent extends InputDirective {
  @Input()
  type = 'text';
}
