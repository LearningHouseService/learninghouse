import { Component, Input, OnInit } from '@angular/core';
import { InputDirective } from '../input/input.directive';

export interface SelectOption {
  value: string;
  label: string;
}

@Component({
  selector: 'learninghouse-select',
  templateUrl: './select.component.html',
  styleUrls: ['./select.component.scss']
})
export class SelectComponent extends InputDirective {

  @Input()
  options: SelectOption[] = [];

}
