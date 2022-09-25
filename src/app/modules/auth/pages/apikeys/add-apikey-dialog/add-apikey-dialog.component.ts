import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, NonNullableFormBuilder, Validators } from '@angular/forms';
import { MatDialogRef } from '@angular/material/dialog';
import { catchError, map } from 'rxjs';
import { AlertType } from 'src/app/shared/components/alert/alert.component';
import { AbstractFormResponse } from 'src/app/shared/components/form-response/form-response.class';
import { APIKeyModel, APIKeyRole, Role } from 'src/app/shared/models/auth.model';
import { AuthService } from '../../../auth.service';
import { AuthValidators } from '../../../auth.validators';
import { ClipboardService } from 'ngx-clipboard';

@Component({
  selector: 'learninghouse-add-apikey',
  templateUrl: './add-apikey-dialog.component.html',
  styleUrls: ['./add-apikey-dialog.component.scss']
})
export class AddAPIKeyDialogComponent extends AbstractFormResponse {

  public AlertType = AlertType;

  form: FormGroup;

  apikey?: APIKeyModel;

  roleOptions = [
    { value: APIKeyRole.user, label: 'common.role.user' },
    { value: APIKeyRole.trainer, label: 'common.role.trainer' }
  ]

  constructor(public dialogRef: MatDialogRef<AddAPIKeyDialogComponent>, private formBuilder: NonNullableFormBuilder, private authService: AuthService, private clipboardService: ClipboardService) {
    super('pages.auth.apikeys.common.success');
    this.form = this.formBuilder.group({
      description: ['', [Validators.required, AuthValidators.APIKeyDescriptionValidator]],
      role: [APIKeyRole.user, [Validators.required]]
    })
  }

  get description(): FormControl {
    return <FormControl>this.form.get('description');
  }

  get role(): FormControl {
    return <FormControl>this.form.get('role');
  }

  onAdd() {
    this.authService.addAPIKey(this.form.value)
      .pipe(
        map((apikey: APIKeyModel) => {
          this.apikey = apikey;
          this.handleSuccess();
        }),
        catchError((error) => this.handleError(error))
      )
      .subscribe()
  }

  onClose() {
    if (this.success$.getValue()) {
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
