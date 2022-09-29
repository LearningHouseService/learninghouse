import { Component } from '@angular/core';
import { FormControl, FormGroup, NonNullableFormBuilder, Validators } from '@angular/forms';
import { catchError, map } from 'rxjs';
import { AbstractFormResponse } from 'src/app/shared/components/form-response/form-response.class';
import { FormResponseConfig } from 'src/app/shared/components/form-response/form-response.component';
import { AuthService } from '../../auth.service';
import { AuthValidators } from '../../auth.validators';

export interface ChangePasswordRequestForm {
  old_password: FormControl<string>;
  new_password: FormControl<string>;
}

export interface ChangePasswordForm {
  api: FormGroup<ChangePasswordRequestForm>,
  confirm_password: FormControl<string>;
}

@Component({
  selector: 'learninghouse-change-password',
  templateUrl: './change-password.component.html',
  styleUrls: ['./change-password.component.scss']
})
export class ChangePasswordComponent extends AbstractFormResponse {

  public form: FormGroup<ChangePasswordForm>;

  public responseConfig: FormResponseConfig = {
    successMessage: 'pages.auth.password.common.success'
  }

  constructor(private formBuilder: NonNullableFormBuilder, private authService: AuthService) {
    super();

    this.form = this.formBuilder.group<ChangePasswordForm>({
      api: this.formBuilder.group<ChangePasswordRequestForm>({
        old_password: this.formBuilder.control('', [Validators.required]),
        new_password: this.formBuilder.control('', [Validators.required])
      }),
      confirm_password: this.formBuilder.control('', [Validators.required])
    }, {
      validators: [AuthValidators.MatchValidator('api.new_password', 'confirm_password')]
    });
  }


  submitChangePassword(): void {
    this.authService.changePassword(this.form.controls.api.getRawValue())
      .pipe(
        map(() => {
          this.authService.loginAdmin({ password: this.form.controls.api.controls.new_password.value })
            .pipe(
              map(() => {
                this.handleSuccess();
              }),
              catchError((error) => this.handleError(error)))
            .subscribe();
        }),
        catchError((error) => this.handleError(error)))
      .subscribe();
  }

}
