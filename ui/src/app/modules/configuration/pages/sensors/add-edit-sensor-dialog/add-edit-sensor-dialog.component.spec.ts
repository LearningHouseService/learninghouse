import { CommonModule } from '@angular/common';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { of } from 'rxjs';
import { EditDialogActionsService } from 'src/app/shared/services/edit-dialog-actions.service';
import { TranslateModule } from '@ngx-translate/core';
import { SensorConfigurationService } from '../../../services/sensor-configuration.service';

import { AddEditSensorDialogComponent } from './add-edit-sensor-dialog.component';

describe('AddEditSensorDialogComponent', () => {
  let component: AddEditSensorDialogComponent;
  let fixture: ComponentFixture<AddEditSensorDialogComponent>;
  const dialogRef = { disableClose: false, close: jasmine.createSpy('close') };
  const configService = {
    createSensor: jasmine.createSpy('createSensor').and.returnValue(of({})),
    updateSensor: jasmine.createSpy('updateSensor').and.returnValue(of({}))
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        CommonModule,
        ReactiveFormsModule,
        TranslateModule.forRoot()
      ],
      declarations: [AddEditSensorDialogComponent],
      providers: [
        { provide: MatDialogRef, useValue: dialogRef },
        { provide: MAT_DIALOG_DATA, useValue: null },
        { provide: SensorConfigurationService, useValue: configService },
        EditDialogActionsService
      ],
      schemas: [NO_ERRORS_SCHEMA]
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
