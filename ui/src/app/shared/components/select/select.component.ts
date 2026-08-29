import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { InputDirective } from '../input/input.directive';

export interface SelectOption<T> {
  value: T;
  label: string;
}

@Component({
  selector: 'learninghouse-select',
  standalone: false,
  templateUrl: './select.component.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrls: ['./select.component.scss']
})
export class SelectComponent<T> extends InputDirective {

  @Input()
  options: SelectOption<T>[] = [];

}
