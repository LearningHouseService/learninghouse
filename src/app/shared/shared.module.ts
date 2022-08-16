import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from '../material.module';
import { InputComponent } from './components/input/input.component';
import { PasswordComponent } from './components/password/password.component';
import { AlertComponent } from './components/alert/alert.component';



@NgModule({
  declarations: [
    InputComponent,
    PasswordComponent,
    AlertComponent
  ],
  imports: [
    CommonModule,
    MaterialModule,
    FormsModule,
    ReactiveFormsModule
  ],
  exports: [
    InputComponent,
    PasswordComponent,
    FormsModule,
    ReactiveFormsModule,
    AlertComponent
  ]
})
export class SharedModule { }
