import { CommonModule } from '@angular/common';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { provideTranslateService, TranslatePipe } from '@ngx-translate/core';

import { PasswordComponent } from './password.component';

describe('PasswordComponent', () => {
  let component: PasswordComponent;
  let fixture: ComponentFixture<PasswordComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        TranslatePipe,
        CommonModule,
        ReactiveFormsModule,
      ],
      providers: [provideTranslateService()],
      declarations: [PasswordComponent],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PasswordComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create with the password hidden by default', () => {
    expect(component).toBeTruthy();
    expect(component.hide).toBeTrue();
  });
});
