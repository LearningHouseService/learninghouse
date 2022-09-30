import { Component, Inject, OnDestroy, OnInit } from '@angular/core';
import { FormControl, FormGroup, NonNullableFormBuilder, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { BehaviorSubject, map, Subject, takeUntil } from 'rxjs';
import { EditDialogConfig, SubmitButtonType } from 'src/app/shared/components/edit-dialog/edit-dialog.component';
import { AbstractFormResponse } from 'src/app/shared/components/form-response/form-response.class';
import { EditDialogActionsService } from 'src/app/shared/services/edit-dialog-actions.service';
import { SensorModel, SensorType } from 'src/app/shared/models/configuration.model';

interface SensorForm {
  name: FormControl<string>;
  typed: FormControl<SensorType>
}

@Component({
  selector: 'app-add-edit-sensor-dialog',
  templateUrl: './add-edit-sensor-dialog.component.html',
  styleUrls: ['./add-edit-sensor-dialog.component.scss']
})
export class AddEditSensorDialogComponent extends AbstractFormResponse implements OnInit, OnDestroy {

  public form: FormGroup<SensorForm>

  public sensor?: SensorModel;

  private isEdit: boolean;

  private destroyed = new Subject<void>();

  public typedOptions = [
    { value: SensorType.NUMERICAL, label: 'common.sensortype.numerical' },
    { value: SensorType.CATEGORICAL, label: 'common.sensortype.categorical' }
  ]

  public dialogConfig: EditDialogConfig;

  constructor(public dialogRef: MatDialogRef<AddEditSensorDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: SensorModel | null,
    private fb: NonNullableFormBuilder,
    private dialogActions: EditDialogActionsService) {

    super();

    this.dialogRef.disableClose = true;

    this.form = this.fb.group<SensorForm>({
      name: this.fb.control<string>('', [Validators.required]),
      typed: this.fb.control<SensorType>(SensorType.NUMERICAL, [Validators.required])
    })

    if (this.data) {
      this.isEdit = true;
      this.dialogConfig = {
        title: 'pages.configuration.sensors.common.edit_dialog_title',
        submitButton$: new BehaviorSubject<SubmitButtonType | null>(SubmitButtonType.EDIT),
        responseConfig: {
          successMessage: 'pages.configuration.sensors.common.success'
        }
      };
    } else {
      this.isEdit = false;
      this.dialogConfig = {
        title: 'pages.configuration.sensors.common.add_dialog_title',
        submitButton$: new BehaviorSubject<SubmitButtonType | null>(SubmitButtonType.ADD),
        responseConfig: {
          successMessage: 'pages.configuration.sensors.common.success'
        }
      };
    }


    this.dialogActions.onClose
      .pipe(
        takeUntil(this.destroyed),
        map(() => this.onClose())
      )
      .subscribe();

  }

  ngOnInit(): void {
    if (this.isEdit) {
      this.form.patchValue(this.data!)
      this.form.controls.name.disable();
    }
  }

  ngOnDestroy(): void {
    this.destroyed.next();
    this.destroyed.complete();
  }

  onClose(): void {
    if (this.isSuccess) {
      this.dialogRef.close(this.form.value as SensorModel);
    } else {
      this.dialogRef.close(null);
    }
  }

}
