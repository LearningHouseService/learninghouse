import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from '../material.module';
import { InputComponent } from './components/input/input.component';



@NgModule({
  declarations: [
    InputComponent
  ],
  imports: [
    CommonModule,
    MaterialModule,
    FormsModule,
    ReactiveFormsModule
  ],
  exports: [
    InputComponent,
    FormsModule,
    ReactiveFormsModule
  ]
})
export class SharedModule { }
