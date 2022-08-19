import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from './material.module';
import { AlertComponent } from './alert/alert.component';
import { InputComponent } from './input/input.component';
import { PasswordComponent } from './password/password.component';
import { SessionTimerComponent } from './session-timer/session-timer.component';

const components = [
  AlertComponent,
  InputComponent,
  PasswordComponent,
  SessionTimerComponent
]

@NgModule({
  declarations: [components],
  imports: [CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MaterialModule],
  exports: [components, MaterialModule]
})
export class ComponentsModule { }
