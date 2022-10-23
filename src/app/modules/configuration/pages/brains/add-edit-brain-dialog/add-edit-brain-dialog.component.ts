import { Component, Inject, OnDestroy, OnInit } from '@angular/core';
import { FormGroup, FormControl, NonNullableFormBuilder, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Subject, BehaviorSubject, takeUntil, map, catchError } from 'rxjs';
import { EditDialogConfig, SubmitButtonType } from 'src/app/shared/components/edit-dialog/edit-dialog.component';
import { AbstractFormResponse } from 'src/app/shared/components/form-response/form-response.class';
import { SelectOption } from 'src/app/shared/components/select/select.component';
import { BrainConfigurationModel, BrainEstimatorType } from 'src/app/shared/models/configuration.model';
import { EditDialogActionsService } from 'src/app/shared/services/edit-dialog-actions.service';
import { GenericValidators } from 'src/app/shared/validators/generic.validators';
import { ConfigurationService } from '../../../configuration.service';

interface BrainConfigurationForm {
  name: FormControl<string>;
  estimator: FormGroup<{
    typed: FormControl<BrainEstimatorType>,
    estimators: FormControl<number>,
    max_depth: FormControl<number>
  }>;
  dependent: FormControl<string>;
  dependent_encode: FormControl<boolean>;
  test_size: FormControl<number>;
}

@Component({
  selector: 'app-add-edit-brain-dialog',
  templateUrl: './add-edit-brain-dialog.component.html',
  styleUrls: ['./add-edit-brain-dialog.component.scss']
})
export class AddEditBrainDialogComponent extends AbstractFormResponse implements OnInit, OnDestroy {

  private static readonly ADD_DIALOG_CONFIG: EditDialogConfig = {
    title: 'pages.configuration.brains.common.add_dialog_title',
    submitButton: SubmitButtonType.ADD,
    responseConfig: {
      successMessage: 'pages.configuration.brains.common.success',
      errorPrefix: 'pages.configuration.brains.errors'
    }
  };

  private static readonly EDIT_DIALOG_CONFIG: EditDialogConfig = {
    ...AddEditBrainDialogComponent.ADD_DIALOG_CONFIG,
    title: 'pages.configuration.brains.common.edit_dialog_title',
    submitButton: SubmitButtonType.EDIT
  };

  public form: FormGroup<BrainConfigurationForm>

  public brainConfiguration?: BrainConfigurationModel;

  private isEdit: boolean;

  private destroyed = new Subject<void>();

  public typedOptions: SelectOption<BrainEstimatorType>[] = [
    { value: BrainEstimatorType.CLASSIFIER, label: 'common.enums.estimatortype.classifier' },
    { value: BrainEstimatorType.REGRESSOR, label: 'common.enums.estimatortype.regressor' }
  ]

  public encodeOptions: SelectOption<boolean>[] = [
    { value: true, label: 'common.buttons.yes' },
    { value: false, label: 'common.buttons.no' }
  ];

  public dialogConfig$ = new BehaviorSubject<EditDialogConfig>(AddEditBrainDialogComponent.ADD_DIALOG_CONFIG);

  constructor(public dialogRef: MatDialogRef<AddEditBrainDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: BrainConfigurationModel | null,
    private fb: NonNullableFormBuilder,
    private configService: ConfigurationService,
    private dialogActions: EditDialogActionsService) {

    super();

    this.dialogRef.disableClose = true;

    this.form = this.fb.group<BrainConfigurationForm>({
      name: this.fb.control<string>('', [Validators.required]),
      estimator: this.fb.group({
        typed: this.fb.control<BrainEstimatorType>(BrainEstimatorType.CLASSIFIER, [Validators.required]),
        estimators: this.fb.control<number>(100, [
          GenericValidators.IntegerValidator,
          Validators.min(100),
          Validators.max(1000)
        ]),
        max_depth: this.fb.control<number>(5, [
          GenericValidators.IntegerValidator,
          Validators.min(4),
          Validators.max(10)
        ])
      }),
      dependent: this.fb.control<string>('', [Validators.required]),
      dependent_encode: this.fb.control<boolean>(false, [Validators.required]),
      test_size: this.fb.control<number>(0.2, [Validators.required, Validators.min(0.1)])
    })

    if (this.data) {
      this.isEdit = true;
      this.dialogConfig$.next(AddEditBrainDialogComponent.EDIT_DIALOG_CONFIG);
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
      this.configService.updateBrain(this.form.getRawValue())
        .pipe(
          map(() => {
            this.handleSuccess();
          }),
          catchError((error) => this.handleError(error))
        )
        .subscribe();
    } else {
      this.configService.createBrain(this.form.getRawValue())
        .pipe(
          map((brain: BrainConfigurationModel) => {
            this.isEdit = true;
            this.data = brain;
            this.form.controls.name.disable();
            this.dialogConfig$.next(AddEditBrainDialogComponent.EDIT_DIALOG_CONFIG);
            this.handleSuccess();
          }),
          catchError((error) => this.handleError(error))
        )
        .subscribe();
    }
  }

  onClose(): void {
    if (this.isSuccess) {
      this.dialogRef.close(this.form.value as BrainConfigurationModel);
    } else {
      this.dialogRef.close(null);
    }
  }
}
