import { Component, Inject, OnDestroy, OnInit } from '@angular/core';
import { FormControl, FormGroup, NonNullableFormBuilder, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { BehaviorSubject, catchError, map, Subject, takeUntil } from 'rxjs';
import { EditDialogConfig, SubmitButtonType } from 'src/app/shared/components/edit-dialog/edit-dialog.component';
import { AbstractFormResponse } from 'src/app/shared/components/form-response/form-response.class';
import { EditDialogActionsService } from 'src/app/shared/services/edit-dialog-actions.service';
import { SensorConfigurationModel, SensorType } from 'src/app/modules/configuration/configuration.model';
import { SensorConfigurationService } from '../../../services/sensor-configuration.service';

interface SensorForm {
  name: FormControl<string>;
  typed: FormControl<SensorType>;
  cycles: FormControl<number>;
  calc_sun_position: FormControl<boolean>;
}

@Component({
  selector: 'app-add-edit-sensor-dialog',
  templateUrl: './add-edit-sensor-dialog.component.html'
})
export class AddEditSensorDialogComponent extends AbstractFormResponse implements OnInit, OnDestroy {

  private static readonly ADD_DIALOG_CONFIG: EditDialogConfig = {
    title: 'pages.configuration.sensors.common.add_dialog_title',
    submitButton: SubmitButtonType.ADD,
    responseConfig: {
      successMessage: 'pages.configuration.sensors.common.success',
      errorPrefix: 'pages.configuration.sensors.errors'
    }
  };

  private static readonly EDIT_DIALOG_CONFIG: EditDialogConfig = {
    ...AddEditSensorDialogComponent.ADD_DIALOG_CONFIG,
    title: 'pages.configuration.sensors.common.edit_dialog_title',
    submitButton: SubmitButtonType.EDIT
  };

  public SensorType = SensorType;

  public form: FormGroup<SensorForm>

  public sensor?: SensorConfigurationModel;

  private isEdit: boolean;

  private destroyed = new Subject<void>();

  public typedOptions = [
    { value: SensorType.NUMERICAL, label: 'common.enums.sensortype.numerical' },
    { value: SensorType.CATEGORICAL, label: 'common.enums.sensortype.categorical' },
    { value: SensorType.CYCLICAL, label: 'common.enums.sensortype.cyclical' },
    { value: SensorType.TIME, label: 'common.enums.sensortype.time' }
  ]

  public dialogConfig$ = new BehaviorSubject<EditDialogConfig>(AddEditSensorDialogComponent.ADD_DIALOG_CONFIG);

  constructor(public dialogRef: MatDialogRef<AddEditSensorDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: SensorConfigurationModel | null,
    private fb: NonNullableFormBuilder,
    private configService: SensorConfigurationService,
    private dialogActions: EditDialogActionsService) {

    super();

    this.dialogRef.disableClose = true;

    this.form = this.fb.group<SensorForm>({
      name: this.fb.control<string>('', [Validators.required]),
      typed: this.fb.control<SensorType>(SensorType.NUMERICAL, [Validators.required]),
      cycles: this.fb.control<number>(0),
      calc_sun_position: this.fb.control<boolean>(false)
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

    this.form.controls.typed.valueChanges
      .pipe(takeUntil(this.destroyed))
      .subscribe(value => {
        this.setConditionalValidators(value);
      });

    this.setConditionalValidators(this.form.controls.typed.value);
  }

  ngOnDestroy(): void {
    this.destroyed.next();
    this.destroyed.complete();
  }

  private setConditionalValidators(typed: SensorType): void {
    const cyclesControl = this.form.controls.cycles;
    const calcSunPositionControl = this.form.controls.calc_sun_position;

    cyclesControl.clearValidators();
    calcSunPositionControl.clearValidators();

    if (typed === SensorType.CYCLICAL) {
      cyclesControl.setValidators([Validators.required]);
    } else if (typed === SensorType.TIME) {
      calcSunPositionControl.setValidators([Validators.required]);
    }

    cyclesControl.updateValueAndValidity();
    calcSunPositionControl.updateValueAndValidity();
  }



  onSubmit(): void {
    if (this.isEdit) {
      this.configService.updateSensor({
        name: this.data!.name,
        typed: this.form.controls.typed.value,
        cycles: this.form.controls.cycles.value,
        calc_sun_position: this.form.controls.calc_sun_position.value
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
          map((sensor: SensorConfigurationModel) => {
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
      this.dialogRef.close(this.form.value as SensorConfigurationModel);
    } else {
      this.dialogRef.close(null);
    }
  }

}
