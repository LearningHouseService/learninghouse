import { CommonModule } from '@angular/common';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideTranslateService, TranslatePipe } from '@ngx-translate/core';

import { SessionTimerComponent } from './session-timer.component';

describe('SessionTimerComponent', () => {
  let component: SessionTimerComponent;
  let fixture: ComponentFixture<SessionTimerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        TranslatePipe,
        CommonModule,
      ],
      providers: [provideTranslateService()],
      declarations: [SessionTimerComponent],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SessionTimerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
