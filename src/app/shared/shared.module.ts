import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';
import { AlertComponent } from './components/alert/alert.component';
import { EditDialogComponent } from './components/edit-dialog/edit-dialog.component';
import { FormResponseComponent } from './components/form-response/form-response.component';
import { InputComponent } from './components/input/input.component';
import { PasswordComponent } from './components/password/password.component';
import { SelectComponent } from './components/select/select.component';
import { SessionTimerComponent } from './components/session-timer/session-timer.component';
import { DeleteDialogComponent } from './components/table/delete-dialog/delete-dialog.component';
import { TableComponent } from './components/table/table.component';
import { MaterialModule } from './material/material.module';

const components = [
  AlertComponent,
  EditDialogComponent,
  FormResponseComponent,
  InputComponent,
  PasswordComponent,
  SelectComponent,
  SessionTimerComponent,
  TableComponent
]


@NgModule({
  declarations: [
    components,
    DeleteDialogComponent],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MaterialModule,
    TranslateModule
  ],
  exports: [
    components,
    FormsModule,
    MaterialModule,
    ReactiveFormsModule,
    TranslateModule
  ]
})
export class SharedModule { }
