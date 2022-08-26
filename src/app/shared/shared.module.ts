import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AlertComponent } from './components/alert/alert.component';
import { InputComponent } from './components/input/input.component';
import { MaterialModule } from './components/material.module';
import { PasswordComponent } from './components/password/password.component';
import { SessionTimerComponent } from './components/session-timer/session-timer.component';

const components = [
  AlertComponent,
  InputComponent,
  PasswordComponent,
  SessionTimerComponent
]


@NgModule({
  declarations: [components],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MaterialModule
  ],
  exports: [
    components,
    FormsModule,
    MaterialModule,
    ReactiveFormsModule
  ]
})
export class SharedModule { }
