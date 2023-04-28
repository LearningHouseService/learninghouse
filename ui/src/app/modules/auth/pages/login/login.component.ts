import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, NonNullableFormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { catchError, map } from 'rxjs';
import { AlertType } from 'src/app/shared/components/alert/alert.component';
import { AbstractFormResponse } from 'src/app/shared/components/form-response/form-response.class';
import { FormResponseConfig } from 'src/app/shared/components/form-response/form-response.component';
import { ServiceMode } from 'src/app/shared/models/api.model';
import { APIService } from 'src/app/shared/services/api.service';
import { AuthService } from '../../auth.service';
import { AuthValidators } from '../../auth.validators';
import { ChangePasswordForm, ChangePasswordRequestForm } from '../change-password/change-password.component';

interface NormalPasswordForm {
  password: FormControl<string>;
}


@Component({
  selector: 'learninghouse-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent extends AbstractFormResponse implements OnInit {

  public AlertType = AlertType;

  public ServiceMode = ServiceMode;

  public normal: FormGroup<NormalPasswordForm>;

  public initial: FormGroup<ChangePasswordForm>;

  readonly responseConfig: FormResponseConfig = {
    successMessage: 'pages.auth.login.common.success'
  };

  constructor(private formBuilder: NonNullableFormBuilder, public api: APIService, private authService: AuthService,
    private router: Router) {
    super();

    this.normal = this.formBuilder.group<NormalPasswordForm>({
      password: this.formBuilder.control('', [Validators.required])
    })

    this.initial = this.formBuilder.group<ChangePasswordForm>({
      api: this.formBuilder.group<ChangePasswordRequestForm>({
        old_password: this.formBuilder.control('', [Validators.required]),
        new_password: this.formBuilder.control('', [Validators.required])
      }),
      confirm_password: this.formBuilder.control('', [Validators.required])
    }, {
      validators: [AuthValidators.MatchValidator('api.new_password', 'confirm_password')]
    });
  }

  ngOnInit(): void {
    this.api.update_mode()
  }

  submitLoginAdmin() {
    this.authService.loginAdmin(this.normal.getRawValue())
      .pipe(
        map(() => {
          this.router.navigate(['/brains/prediction']);
        }),
        catchError((error) => this.handleError(error))
      )
      .subscribe();
  }

  submitLoginAPIKey() {
    this.authService.loginAPIKey(this.normal.controls.password.value)
      .pipe(
        map(() => {
          this.router.navigate(['/brains/prediction']);
        }),
        catchError((error) => this.handleError(error))
      )
      .subscribe();
  }

  submitInitial() {
    this.authService.loginAdmin({ password: this.initial.controls.api.controls.old_password.value })
      .pipe(
        map(() => {
          this.authService.changePassword(this.initial.controls.api.getRawValue())
            .pipe(
              map(() => {
                this.authService.loginAdmin({ password: this.initial.controls.api.controls.new_password.value })
                  .pipe(
                    map(() => {
                      this.handleSuccess();
                      this.router.navigate(['/brains/prediction']);
                    }),
                    catchError((error) => this.handleError(error)))
                  .subscribe();
              }),
              catchError((error) => this.handleError(error)))
            .subscribe();
        }),
        catchError((error) => this.handleError(error)))
      .subscribe();
  }

}
