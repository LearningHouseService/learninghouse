import { CommonModule } from '@angular/common';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatDialog } from '@angular/material/dialog';
import { MatSortModule } from '@angular/material/sort';
import { TranslateModule } from '@ngx-translate/core';
import { of } from 'rxjs';
import { TableActionsService } from 'src/app/shared/services/table-actions.service';
import { SensorConfigurationService } from '../../services/sensor-configuration.service';

import { SensorsComponent } from './sensors.component';

describe('SensorsComponent', () => {
  let component: SensorsComponent;
  let fixture: ComponentFixture<SensorsComponent>;
  const configService = {
    getSensors: jasmine.createSpy('getSensors').and.returnValue(of([])),
    deleteSensor: jasmine.createSpy('deleteSensor').and.returnValue(of({ name: 'x' }))
  };
  const dialog = jasmine.createSpyObj<MatDialog>('MatDialog', ['open']);

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        CommonModule,
        MatSortModule,
        TranslateModule.forRoot()
      ],
      declarations: [SensorsComponent],
      providers: [
        { provide: MatDialog, useValue: dialog },
        { provide: SensorConfigurationService, useValue: configService },
        TableActionsService
      ],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SensorsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create and load the sensors', () => {
    expect(component).toBeTruthy();
    expect(configService.getSensors).toHaveBeenCalled();
  });
});
