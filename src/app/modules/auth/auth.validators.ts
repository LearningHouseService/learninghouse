import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

export class AuthValidators {
    static MatchValidator(source: string, target: string): ValidatorFn {
        return (control: AbstractControl): ValidationErrors | null => {
            const sourceCtrl = control.get(source);
            const targetCtrl = control.get(target);

            const error = sourceCtrl && targetCtrl && sourceCtrl.value !== targetCtrl.value
                ? { confirmMismatch: true }
                : null;

            targetCtrl?.setErrors(error);

            return error;
        };
    }
}