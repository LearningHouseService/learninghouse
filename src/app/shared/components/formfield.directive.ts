import { Input, OnInit, Directive } from '@angular/core';
import { AbstractControl, FormControl } from '@angular/forms';

@Directive()
export class FormFieldDirective implements OnInit {
    @Input()
    control: FormControl = new FormControl();

    @Input()
    required = false;

    @Input()
    name = '';

    @Input()
    maxlength?: number;

    ngOnInit(): void {
        if (this.control.validator) {
            const validator = this.control.validator({} as AbstractControl);
            this.required = validator !== null && validator['required'] === true;
        }
    }

    showErrors(): string {
        let error = '';

        if (this.control.errors) {
            if (this.control.errors['required']) {
                error = 'Fill required field';
            }
        }

        return error;
    }

}