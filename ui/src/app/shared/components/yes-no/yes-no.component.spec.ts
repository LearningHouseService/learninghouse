import { CommonModule } from '@angular/common';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { provideTranslateService, TranslatePipe } from '@ngx-translate/core';

import { YesNoComponent } from './yes-no.component';

describe('YesNoComponent', () => {
  let component: YesNoComponent;
  let fixture: ComponentFixture<YesNoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        TranslatePipe,
        CommonModule,
        ReactiveFormsModule,
      ],
      providers: [provideTranslateService()],
      declarations: [YesNoComponent],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();

    fixture = TestBed.createComponent(YesNoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create with a yes and a no option', () => {
    expect(component).toBeTruthy();
    expect(component.yesNoOptions).toEqual([
      { value: true, label: 'common.buttons.yes' },
      { value: false, label: 'common.buttons.no' }
    ]);
  });
});
