import { Component, OnDestroy, OnInit } from '@angular/core';
import { NonNullableFormBuilder, FormGroup, Validators, FormControl } from '@angular/forms';
import { LearningHouseError, ServiceMode } from 'src/app/shared/models/api.model';
import { APIService } from 'src/app/shared/services/api.service';
import { AlertType } from 'src/app/shared/components/alert/alert.component';
import { AuthService } from '../../auth.service';
import { BehaviorSubject, catchError, map, of } from 'rxjs';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {

  form: FormGroup;

  loginError$ = new BehaviorSubject<string | null>(null);

  constructor(private formBuilder: NonNullableFormBuilder, public api: APIService, private authService: AuthService,
    private router: Router) {
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
          this.api.put<boolean>('/auth/password', this.initial.value)
            .pipe(
              map(() => {
                this.authService.loginAdmin({ password: this.new_password.value })
                  .pipe(
                    map(() => {
                      this.loginError$.next(null);
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

  handleError(error: LearningHouseError) {
    this.loginError$.next(error.key);
    return of(false);
  }

  get ServiceMode() {
    return ServiceMode;
  }

  get AlertType() {
    return AlertType;
  }

}
