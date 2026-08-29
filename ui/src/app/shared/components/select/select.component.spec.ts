import { CommonModule } from '@angular/common';
import { FocusMonitor } from '@angular/cdk/a11y';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MAT_FORM_FIELD } from '@angular/material/form-field';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { provideTranslateService, TranslatePipe } from '@ngx-translate/core';
import { ButtonGroupComponent } from '../button-group/button-group.component';

import { SelectComponent } from './select.component';

describe('SelectComponent', () => {
  let component: SelectComponent<string>;
  let fixture: ComponentFixture<SelectComponent<string>>;

  beforeEach(async () => {
    // Zero (the default) or two options renders <learninghouse-button-group>, which needs
    // to be a real, declared ControlValueAccessor for [formControl] to resolve - same setup
    // as button-group.component.spec.ts.
    await TestBed.configureTestingModule({
      imports: [
        TranslatePipe,
        CommonModule,
        ReactiveFormsModule,
        NoopAnimationsModule,
        MatButtonToggleModule,
      ],
      declarations: [SelectComponent, ButtonGroupComponent],
      providers: [
        provideTranslateService(),
        {
          provide: FocusMonitor, useValue: {
            stopMonitoring: () => undefined,
            focusVia: () => undefined
          }
        },
        { provide: MAT_FORM_FIELD, useValue: { getLabelId: () => 'select-label' } }
      ],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SelectComponent<string>);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create with no options by default', () => {
    expect(component).toBeTruthy();
    expect(component.options).toEqual([]);
  });
});
