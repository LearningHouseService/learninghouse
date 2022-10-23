import { ThisReceiver } from '@angular/compiler';
import { Directive, Input, OnInit } from '@angular/core';
import { FormControl, Validators } from '@angular/forms';
import { TranslateCompiler, TranslateService } from '@ngx-translate/core';

@Directive()
export class FormFieldDirective implements OnInit {
    @Input()
    control: FormControl = new FormControl();

    @Input()
    required = false;

    @Input()
    name = '';

    constructor(private translate: TranslateService) { }

    ngOnInit(): void {
        if (this.control.validator) {
            this.required = this.control.hasValidator(Validators.required);
        }
    }

    errorTranslations(): string[] {
        return Object.keys(this.control.errors || {})
            .map((key) => {
                const error = this.control.errors![key];
                let translation = 'components.input.errors.' + key;
                let param = null;

                switch (key) {
                    case 'min':
                        param = error['min'];
                        break;
                    case 'max':
                        param = error['max'];
                        break;
                    default:
                        if (typeof error === 'string') {
                            translation = error;
                        }

                }

                if (param) {
                    translation = this.translate.instant(translation, { param: param });
                } else {
                    translation = this.translate.instant(translation);
                }

                return translation;
            });
    }

}