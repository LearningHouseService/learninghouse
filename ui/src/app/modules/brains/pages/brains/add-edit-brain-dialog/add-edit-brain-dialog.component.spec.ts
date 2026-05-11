import { CommonModule } from '@angular/common';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { TranslateModule } from '@ngx-translate/core';
import { of } from 'rxjs';
import { EditDialogActionsService } from 'src/app/shared/services/edit-dialog-actions.service';
import { BrainsService } from '../../../brains.service';

import { AddEditBrainDialogComponent } from './add-edit-brain-dialog.component';

describe('AddEditBrainDialogComponent', () => {
  let component: AddEditBrainDialogComponent;
  let fixture: ComponentFixture<AddEditBrainDialogComponent>;
  const dialogRef = { disableClose: false, close: jasmine.createSpy('close') };
  const brainsService = {
    createBrain: jasmine.createSpy('createBrain').and.returnValue(of({})),
    updateBrain: jasmine.createSpy('updateBrain').and.returnValue(of({}))
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        CommonModule,
        ReactiveFormsModule,
        TranslateModule.forRoot()
      ],
      declarations: [AddEditBrainDialogComponent],
      providers: [
        { provide: MatDialogRef, useValue: dialogRef },
        { provide: MAT_DIALOG_DATA, useValue: null },
        { provide: BrainsService, useValue: brainsService },
        EditDialogActionsService
      ],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddEditBrainDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
