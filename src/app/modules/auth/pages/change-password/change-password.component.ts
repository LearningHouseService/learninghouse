import { Component } from '@angular/core';
import { FormControl, FormGroup, NonNullableFormBuilder, Validators } from '@angular/forms';
import { catchError, map } from 'rxjs';
import { AbstractFormResponse } from 'src/app/shared/components/form-response/form-response.class';
import { AuthService } from '../../auth.service';
import { AuthValidators } from '../../auth.validators';

@Component({
  selector: 'app-change-password',
  templateUrl: './change-password.component.html',
  styleUrls: ['./change-password.component.scss']
})
export class ChangePasswordComponent extends AbstractFormResponse {

  public form: FormGroup;

  constructor(private formBuilder: NonNullableFormBuilder, private authService: AuthService) {
    super('pages.auth.password.common.success');
    this.form = this.formBuilder.group({
      changePassword: this.formBuilder.group({
        old_password: ['', [Validators.required]],
        new_password: ['', [Validators.required]]
      }),
      confirm_password: ['', [Validators.required]]
    }, {
      validators: [AuthValidators.MatchValidator('changePassword.new_password', 'confirm_password')]
    });
  }

  get changePassword(): FormGroup {
    return <FormGroup>this.form.get('changePassword');
  }

  get old_password(): FormControl {
    return <FormControl>this.form.get('changePassword.old_password');
  }

  get new_password(): FormControl {
    return <FormControl>this.form.get('changePassword.new_password');
  }

  get confirm_password(): FormControl {
    return <FormControl>this.form.get('confirm_password');
  }

  submitChangePassword(): void {
    this.success$.next(false);
    this.authService.changePassword(this.changePassword.value)
      .pipe(
        map(() => {
          this.authService.loginAdmin({ password: this.new_password.value })
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
