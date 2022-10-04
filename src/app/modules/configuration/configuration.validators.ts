import { AbstractControl, ValidationErrors } from "@angular/forms";

export class ConfigurationValidators {

    static readonly INTEGER_PATTERN = /^[1-9]+\d*$/

    static EstimatorsValidator(control: AbstractControl): ValidationErrors | null {
        let result = null;

        const value = control.value;

        if (value) {
            if (!ConfigurationValidators.INTEGER_PATTERN.test(value)) {
                result = {
                    integer: true
                };
            } else {
                const intValue = parseInt(value);
                if (intValue < 100) {
                    result = {
                        estimatorsMin: 'pages.configuration.brains.errors.estimatorsMin'
                    };
                } else if (intValue > 1000) {
                    result = {
                        estimatorsMax: 'pages.configuration.brains.errors.estimatorsMax'
                    }
                }
            }
        }

        return result;
    }
}