import { Directive, Input, OnInit } from '@angular/core';
import { FormControl, Validators } from '@angular/forms';

@Directive()
export class FormFieldDirective implements OnInit {
    @Input()
    control: FormControl = new FormControl();

    @Input()
    required = false;

    @Input()
    name = '';


    ngOnInit(): void {
        if (this.control.validator) {
            this.required = this.control.hasValidator(Validators.required);
        }
    }

    errorTranslationKeys(): string[] {
        return Object.keys(this.control.errors || {})
            .map(key => 'components.input.errors.' + key);
    }

}