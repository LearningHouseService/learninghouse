import { Input, OnInit, Directive } from '@angular/core';
import { AbstractControl, FormControl, Validators } from '@angular/forms';

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