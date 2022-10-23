import { Component, OnDestroy } from '@angular/core';
import { FormControl, FormGroup, NonNullableFormBuilder, Validators } from '@angular/forms';
import { MatDialogRef } from '@angular/material/dialog';
import { ClipboardService } from 'ngx-clipboard';
import { BehaviorSubject, catchError, map, Subject, takeUntil } from 'rxjs';
import { AlertType } from 'src/app/shared/components/alert/alert.component';
import { EditDialogConfig, SubmitButtonType } from 'src/app/shared/components/edit-dialog/edit-dialog.component';
import { AbstractFormResponse } from 'src/app/shared/components/form-response/form-response.class';
import { APIKeyModel, APIKeyRole } from 'src/app/shared/models/auth.model';
import { EditDialogActionsService } from 'src/app/shared/services/edit-dialog-actions.service';
import { AuthService } from '../../../auth.service';
import { AuthValidators } from '../../../auth.validators';


interface APIKeyForm {
  description: FormControl<string>;
  role: FormControl<APIKeyRole>;
}
@Component({
  selector: 'learninghouse-add-apikey',
  templateUrl: './add-apikey-dialog.component.html',
  styleUrls: ['./add-apikey-dialog.component.scss']
})
export class AddAPIKeyDialogComponent extends AbstractFormResponse implements OnDestroy {

  public AlertType = AlertType;

  public form: FormGroup<APIKeyForm>;

  public apikey?: APIKeyModel;

  private destroyed = new Subject<void>();

  public roleOptions = [
    { value: APIKeyRole.USER, label: 'common.enums.role.user' },
    { value: APIKeyRole.TRAINER, label: 'common.enums.role.trainer' }
  ]

  private static readonly NO_ADD_DIALOG_CONFIG = {
    title: 'pages.auth.apikeys.common.dialog_title',
    responseConfig: {
      successMessage: 'pages.auth.apikeys.common.success'
    }
  };

  private static readonly ADD_DIALOG_CONFIG = {
    ...AddAPIKeyDialogComponent.NO_ADD_DIALOG_CONFIG,
    submitButton: SubmitButtonType.ADD
  };

  public dialogConfig$ = new BehaviorSubject<EditDialogConfig>(AddAPIKeyDialogComponent.ADD_DIALOG_CONFIG);

  constructor(public dialogRef: MatDialogRef<AddAPIKeyDialogComponent>,
    private fb: NonNullableFormBuilder,
    private authService: AuthService,
    private clipboardService: ClipboardService,
    private dialogActions: EditDialogActionsService) {

    super();

    this.dialogRef.disableClose = true;

    this.form = this.fb.group<APIKeyForm>({
      description: this.fb.control<string>('', [Validators.required, AuthValidators.APIKeyDescriptionValidator]),
      role: this.fb.control<APIKeyRole>(APIKeyRole.USER, [Validators.required])
    })

    this.dialogActions.onSubmit
      .pipe(
        takeUntil(this.destroyed),
        map(() => this.onAdd())
      )
      .subscribe();

    this.dialogActions.onClose
      .pipe(
        takeUntil(this.destroyed),
        map(() => this.onClose())
      )
      .subscribe();
  }

  ngOnDestroy(): void {
    this.destroyed.next()
    this.destroyed.complete();
  }

  onAdd() {
    this.authService.addAPIKey(this.form.getRawValue())
      .pipe(
        map((apikey: APIKeyModel) => {
          this.apikey = apikey;
          this.dialogConfig$.next(AddAPIKeyDialogComponent.NO_ADD_DIALOG_CONFIG);
          this.form.disable();
          this.handleSuccess();
        }),
        catchError((error) => this.handleError(error))
      )
      .subscribe()
  }

  onClose() {
    if (this.isSuccess) {
      this.dialogRef.close(this.form.value as APIKeyModel);
    } else {
      this.dialogRef.close(null);
    }
  }

  copyToClipboard() {
    if (this.apikey?.key) {
      this.clipboardService.copy(this.apikey?.key);
    }
  }

}
