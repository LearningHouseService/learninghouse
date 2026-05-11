import { CommonModule } from '@angular/common';
import { FocusMonitor } from '@angular/cdk/a11y';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MAT_FORM_FIELD } from '@angular/material/form-field';
import { TranslateModule } from '@ngx-translate/core';

import { ButtonGroupComponent } from './button-group.component';

describe('ButtonGroupComponent', () => {
  let component: ButtonGroupComponent<unknown>;
  let fixture: ComponentFixture<ButtonGroupComponent<unknown>>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        CommonModule,
        ReactiveFormsModule,
        NoopAnimationsModule,
        MatButtonToggleModule,
        TranslateModule.forRoot()
      ],
      declarations: [ButtonGroupComponent],
      providers: [
        {
          provide: FocusMonitor, useValue: {
            stopMonitoring: () => undefined,
            focusVia: () => undefined
          }
        },
        { provide: MAT_FORM_FIELD, useValue: { getLabelId: () => 'button-group-label' } }
      ],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ButtonGroupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
