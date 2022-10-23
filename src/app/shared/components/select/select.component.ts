import { Component, Input } from '@angular/core';
import { InputDirective } from '../input/input.directive';

export interface SelectOption<T> {
  value: T;
  label: string;
}

@Component({
  selector: 'learninghouse-select',
  templateUrl: './select.component.html',
  styleUrls: ['./select.component.scss']
})
export class SelectComponent<T> extends InputDirective {

  @Input()
  options: SelectOption<T>[] = [];

}
