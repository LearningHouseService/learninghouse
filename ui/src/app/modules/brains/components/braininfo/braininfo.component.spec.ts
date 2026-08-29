import { CommonModule } from '@angular/common';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideTranslateService, TranslatePipe } from '@ngx-translate/core';

import { BraininfoComponent } from './braininfo.component';

describe('BraininfoComponent', () => {
  let component: BraininfoComponent;
  let fixture: ComponentFixture<BraininfoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        TranslatePipe,
        CommonModule,
      ],
      providers: [provideTranslateService()],
      declarations: [BraininfoComponent],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BraininfoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
