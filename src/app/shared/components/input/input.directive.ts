import { Directive, EventEmitter, Input, Output } from '@angular/core';
import { FormFieldDirective } from '../formfield.directive';

@Directive()
export class InputDirective extends FormFieldDirective {
    @Input()
    maxlength?: number;

    @Input()
    clickableSuffixIcon?: string

    @Output()
    clickSuffix = new EventEmitter<void>()

}