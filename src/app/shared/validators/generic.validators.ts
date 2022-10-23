import { AbstractControl, ValidationErrors } from "@angular/forms";

export class GenericValidators {
    static readonly INTEGER_PATTERN = /^[1-9]+\d*$/

    static IntegerValidator(control: AbstractControl): ValidationErrors | null {
        let result = null;

        if (control.value && !GenericValidators.INTEGER_PATTERN.test(control.value)) {
            result = {
                integer: true
            };
        }

        return result;
    }
}