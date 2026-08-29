import { CommonModule } from '@angular/common';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { provideTranslateService, TranslatePipe } from '@ngx-translate/core';
import { of } from 'rxjs';
import { AuthService } from '../../auth.service';

import { ChangePasswordComponent } from './change-password.component';

describe('ChangePasswordComponent', () => {
  let component: ChangePasswordComponent;
  let fixture: ComponentFixture<ChangePasswordComponent>;
  const authService = {
    changePassword: jasmine.createSpy('changePassword').and.returnValue(of(true)),
    loginAdmin: jasmine.createSpy('loginAdmin').and.returnValue(of({}))
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        TranslatePipe,
        CommonModule,
        ReactiveFormsModule,
      ],
      declarations: [ChangePasswordComponent],
      providers: [
        provideTranslateService(),
        { provide: AuthService, useValue: authService }
      ],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChangePasswordComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
