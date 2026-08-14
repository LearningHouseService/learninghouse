import { CommonModule } from '@angular/common';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TranslateModule } from '@ngx-translate/core';

import { FormResponseComponent } from './form-response.component';

describe('FormResponseComponent', () => {
  let component: FormResponseComponent;
  let fixture: ComponentFixture<FormResponseComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        CommonModule,
        TranslateModule.forRoot()
      ],
      declarations: [FormResponseComponent],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FormResponseComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create without ever assigning a config', () => {
    // The defaulting logic lives in the config setter, so it only applies once
    // something actually assigns to it - a component nobody binds [config] to
    // keeps the bare private default.
    expect(component).toBeTruthy();
    expect(component.config).toEqual({});
  });

  it('should fill in the common success message and error prefix when config is assigned', () => {
    component.config = {};

    expect(component.config).toEqual({
      successMessage: 'common.messages.success',
      errorPrefix: 'common.errors'
    });
  });

  it('should let an explicit config override only the given keys', () => {
    component.config = { successMessage: 'pages.auth.login.common.success' };

    expect(component.config).toEqual({
      successMessage: 'pages.auth.login.common.success',
      errorPrefix: 'common.errors'
    });
  });
});
