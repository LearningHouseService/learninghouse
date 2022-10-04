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
            .map((key) => {
                const error = this.control.errors![key];
                let translationKey = 'components.input.errors.' + key;

                if (typeof error === 'string') {
                    translationKey = error;
                }

                return translationKey;
            })
    }

}