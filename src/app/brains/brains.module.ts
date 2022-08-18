import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TrainingComponent } from './training/training.component';
import { PredictionComponent } from './prediction/prediction.component';
import { BrainsRoutingModule } from './brains-routing.module';
import { RouterModule } from '@angular/router';



@NgModule({
  declarations: [
    TrainingComponent,
    PredictionComponent
  ],
  imports: [
    CommonModule,
    BrainsRoutingModule,
    RouterModule
  ]
})
export class BrainsModule { }
