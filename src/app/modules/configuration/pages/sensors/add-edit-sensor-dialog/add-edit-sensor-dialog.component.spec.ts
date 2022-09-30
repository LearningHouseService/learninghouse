import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddEditSensorDialogComponent } from './add-edit-sensor-dialog.component';

describe('AddEditSensorDialogComponent', () => {
  let component: AddEditSensorDialogComponent;
  let fixture: ComponentFixture<AddEditSensorDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AddEditSensorDialogComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddEditSensorDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
