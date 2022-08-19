import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ComponentsModule } from './components/components.module';
import { MaterialModule } from './components/material.module';



@NgModule({
  imports: [
    FormsModule,
    ReactiveFormsModule,
    ComponentsModule
  ],
  exports: [
    FormsModule,
    ReactiveFormsModule,
    ComponentsModule
  ]
})
export class SharedModule { }
