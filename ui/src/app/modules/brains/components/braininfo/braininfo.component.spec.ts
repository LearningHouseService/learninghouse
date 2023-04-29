import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BraininfoComponent } from './braininfo.component';

describe('BraininfoComponent', () => {
  let component: BraininfoComponent;
  let fixture: ComponentFixture<BraininfoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BraininfoComponent ]
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
