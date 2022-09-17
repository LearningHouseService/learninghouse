import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';
import { AlertComponent } from './components/alert/alert.component';
import { FormResponseComponent } from './components/form-response/form-response.component';
import { InputComponent } from './components/input/input.component';
import { MaterialModule } from './material/material.module';
import { PasswordComponent } from './components/password/password.component';
import { SessionTimerComponent } from './components/session-timer/session-timer.component';
import { TableComponent } from './components/table/table.component';
import { SelectComponent } from './components/select/select.component';

const components = [
  AlertComponent,
  FormResponseComponent,
  InputComponent,
  PasswordComponent,
  SelectComponent,
  SessionTimerComponent,
  TableComponent
]


@NgModule({
  declarations: [components],
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
