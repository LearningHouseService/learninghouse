import { Directive, Input, OnDestroy, OnInit } from '@angular/core';
import { FormControl, Validators } from '@angular/forms';
import { TranslateService } from '@ngx-translate/core';
import { Subject, takeUntil } from 'rxjs';

@Directive()
export class FormFieldDirective implements OnInit, OnDestroy {
    @Input()
    control: FormControl = new FormControl();

    @Input()
    required = false;

    @Input()
    name = '';

    private destroyed = new Subject<void>();

    constructor(private translate: TranslateService) { }

    ngOnInit(): void {
        this.updateRequiredStatus()

        this.control.valueChanges
            .pipe(takeUntil(this.destroyed))
            .subscribe(value => {
                this.updateRequiredStatus();
            });


        this.control.statusChanges
            .pipe(takeUntil(this.destroyed))
            .subscribe(value => {
                this.updateRequiredStatus();
            });

    }

    ngOnDestroy(): void {
        this.destroyed.next();
        this.destroyed.complete();
    }


    private updateRequiredStatus(): void {
        this.required = this.control.validator != null && this.control.hasValidator(Validators.required);
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