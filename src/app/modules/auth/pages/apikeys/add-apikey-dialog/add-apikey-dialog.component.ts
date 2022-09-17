import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, NonNullableFormBuilder, Validators } from '@angular/forms';
import { MatDialogRef } from '@angular/material/dialog';
import { AbstractFormResponse } from 'src/app/shared/components/form-response/form-response.class';
import { Role } from 'src/app/shared/models/auth.model';

@Component({
  selector: 'learninghouse-add-apikey',
  templateUrl: './add-apikey-dialog.component.html',
  styleUrls: ['./add-apikey-dialog.component.scss']
})
export class AddAPIKeyDialogComponent extends AbstractFormResponse {

  form: FormGroup;

  roleOptions = [
    { value: Role.USER.label, label: 'common.role.' + Role.USER },
    { value: Role.TRAINER.label, label: 'common.role.' + Role.TRAINER }
  ]

  constructor(public dialogRef: MatDialogRef<AddAPIKeyDialogComponent>, private formBuilder: NonNullableFormBuilder) {
    super('pages.auth.apikeys.common.success');
    this.form = this.formBuilder.group({
      description: ['', [Validators.required]],
      role: ['', [Validators.required]]
    })
  }

  get description(): FormControl {
    return <FormControl>this.form.get('description');
  }

  get role(): FormControl {
    return <FormControl>this.form.get('role');
  }

}
