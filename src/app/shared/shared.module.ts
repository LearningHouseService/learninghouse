import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from '../material.module';
import { InputComponent } from './components/input/input.component';
import { PasswordComponent } from './components/password/password.component';



@NgModule({
  declarations: [
    InputComponent,
    PasswordComponent
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
    ReactiveFormsModule
  ]
})
export class SharedModule { }
