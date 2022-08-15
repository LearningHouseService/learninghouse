import { Directive, Input } from '@angular/core';
import { FormFieldDirective } from '../formfield.directive';

@Directive()
export class InputDirective extends FormFieldDirective {
    @Input()
    maxlength?: number;

}