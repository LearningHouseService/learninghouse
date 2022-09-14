import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, NonNullableFormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { catchError, map } from 'rxjs';
import { AlertType } from 'src/app/shared/components/alert/alert.component';
import { AbstractFormResponse } from 'src/app/shared/components/form-response/form-response.class';
import { ServiceMode } from 'src/app/shared/models/api.model';
import { APIService } from 'src/app/shared/services/api.service';
import { AuthService } from '../../auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent extends AbstractFormResponse implements OnInit {

  public AlertType = AlertType;

  public ServiceMode = ServiceMode;

  private form: FormGroup;

  constructor(private formBuilder: NonNullableFormBuilder, public api: APIService, private authService: AuthService,
    private router: Router) {
    super('pages.auth.login.common.success');
    this.form = this.formBuilder.group({
      normal: this.formBuilder.group({
        password: ['', [Validators.required]]
      }),
      initial: this.formBuilder.group({
        old_password: ['', [Validators.required]],
        new_password: ['', [Validators.required]]
      })

    });
  }

  ngOnInit(): void {
    this.api.update_mode()
  }

  get normal(): FormGroup {
    return <FormGroup>this.form.get('normal');
  }

  get password(): FormControl {
    return <FormControl>this.form.get('normal.password');
  }

  get initial(): FormGroup {
    return <FormGroup>this.form.get('initial');
  }

  get old_password(): FormControl {
    return <FormControl>this.form.get('initial.old_password');
  }

  get new_password(): FormControl {
    return <FormControl>this.form.get('initial.new_password');
  }

  submitLoginAdmin() {
    this.authService.loginAdmin(this.normal.value)
      .pipe(
        map(() => {
          this.router.navigate(['/dashboard']);
        }),
        catchError((error) => this.handleError(error))
      )
      .subscribe();
  }

  submitLoginAPIKey() {
    this.authService.loginAPIKey(this.password.value)
      .pipe(
        map(() => {
          this.router.navigate(['/dashboard']);
        }),
        catchError((error) => this.handleError(error))
      )
      .subscribe();
  }

  submitInitial() {
    this.authService.loginAdmin({ password: this.old_password.value })
      .pipe(
        map(() => {
          this.authService.changePassword(this.initial.value)
            .pipe(
              map(() => {
                this.authService.loginAdmin({ password: this.new_password.value })
                  .pipe(
                    map(() => {
                      this.handleSuccess();
                      this.router.navigate(['/dashboard']);
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
