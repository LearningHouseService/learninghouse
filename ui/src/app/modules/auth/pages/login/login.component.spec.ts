import { CommonModule } from '@angular/common';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { provideTranslateService, TranslatePipe } from '@ngx-translate/core';
import { BehaviorSubject, of } from 'rxjs';
import { ServiceMode } from 'src/app/shared/models/api.model';
import { APIService } from 'src/app/shared/services/api.service';
import { AuthService } from '../../auth.service';

import { LoginComponent } from './login.component';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;
  const api = {
    mode$: new BehaviorSubject(ServiceMode.PRODUCTION),
    update_mode: jasmine.createSpy('update_mode')
  };
  const authService = {
    loginAdmin: jasmine.createSpy('loginAdmin').and.returnValue(of({})),
    loginAPIKey: jasmine.createSpy('loginAPIKey').and.returnValue(of({})),
    changePassword: jasmine.createSpy('changePassword').and.returnValue(of(true))
  };
  const router = jasmine.createSpyObj<Router>('Router', ['navigate']);

  beforeEach(async () => {
    router.navigate.and.returnValue(Promise.resolve(true));

    await TestBed.configureTestingModule({
      imports: [
        TranslatePipe,
        CommonModule,
        ReactiveFormsModule,
      ],
      declarations: [LoginComponent],
      providers: [
        provideTranslateService(),
        { provide: APIService, useValue: api },
        { provide: AuthService, useValue: authService },
        { provide: Router, useValue: router }
      ],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
    expect(api.update_mode).toHaveBeenCalled();
  });
});
