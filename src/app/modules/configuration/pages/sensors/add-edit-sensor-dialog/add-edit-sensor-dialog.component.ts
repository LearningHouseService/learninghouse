import { Component, Inject, OnDestroy, OnInit } from '@angular/core';
import { FormControl, FormGroup, NonNullableFormBuilder, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { BehaviorSubject, catchError, map, Subject, takeUntil } from 'rxjs';
import { EditDialogConfig, SubmitButtonType } from 'src/app/shared/components/edit-dialog/edit-dialog.component';
import { AbstractFormResponse } from 'src/app/shared/components/form-response/form-response.class';
import { EditDialogActionsService } from 'src/app/shared/services/edit-dialog-actions.service';
import { SensorModel, SensorType } from 'src/app/shared/models/configuration.model';
import { ConfigurationService } from '../../../configuration.service';

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

  private static readonly ADD_DIALOG_CONFIG = {
    title: 'pages.configuration.sensors.common.add_dialog_title',
    submitButton: SubmitButtonType.ADD,
    responseConfig: {
      successMessage: 'pages.configuration.sensors.common.success',
      errorPrefix: 'pages.configuration.sensors.errors'
    }
  };

  private static readonly EDIT_DIALOG_CONFIG = {
    ...AddEditSensorDialogComponent.ADD_DIALOG_CONFIG,
    submitButton: SubmitButtonType.EDIT
  };

  public form: FormGroup<SensorForm>

  public sensor?: SensorModel;

  private isEdit: boolean;

  private destroyed = new Subject<void>();

  public typedOptions = [
    { value: SensorType.NUMERICAL, label: 'common.enums.sensortype.numerical' },
    { value: SensorType.CATEGORICAL, label: 'common.enums.sensortype.categorical' }
  ]

  public dialogConfig$ = new BehaviorSubject<EditDialogConfig>(AddEditSensorDialogComponent.ADD_DIALOG_CONFIG);

  constructor(public dialogRef: MatDialogRef<AddEditSensorDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: SensorModel | null,
    private fb: NonNullableFormBuilder,
    private configService: ConfigurationService,
    private dialogActions: EditDialogActionsService) {

    super();

    this.dialogRef.disableClose = true;

    this.form = this.fb.group<SensorForm>({
      name: this.fb.control<string>('', [Validators.required]),
      typed: this.fb.control<SensorType>(SensorType.NUMERICAL, [Validators.required])
    })

    if (this.data) {
      this.isEdit = true;
      this.dialogConfig$.next(AddEditSensorDialogComponent.EDIT_DIALOG_CONFIG);
    } else {
      this.isEdit = false;
    }

    this.dialogActions.onSubmit
      .pipe(
        takeUntil(this.destroyed),
        map(() => this.onSubmit())
      )
      .subscribe();

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

  onSubmit(): void {
    if (this.isEdit) {
      this.configService.updateSensor({
        name: this.data!.name,
        typed: this.form.controls.typed.value
      })
        .pipe(
          map(() => {
            this.handleSuccess();
          }),
          catchError((error) => this.handleError(error))
        )
        .subscribe();
    } else {
      this.configService.createSensor(this.form.getRawValue())
        .pipe(
          map((sensor: SensorModel) => {
            this.isEdit = true;
            this.data = sensor;
            this.form.controls.name.disable();
            this.dialogConfig$.next(AddEditSensorDialogComponent.EDIT_DIALOG_CONFIG);
            this.handleSuccess();
          }),
          catchError((error) => this.handleError(error))
        )
        .subscribe();
    }
  }

  onClose(): void {
    if (this.isSuccess) {
      this.dialogRef.close(this.form.value as SensorModel);
    } else {
      this.dialogRef.close(null);
    }
  }

}
