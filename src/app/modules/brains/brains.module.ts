import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TrainingComponent } from './pages/training/training.component';
import { PredictionComponent } from './pages/prediction/prediction.component';
import { BrainsRoutingModule } from './brains.routes';
import { RouterModule } from '@angular/router';
import { SharedModule } from 'src/app/shared/shared.module';



@NgModule({
  declarations: [
    TrainingComponent,
    PredictionComponent
  ],
  imports: [
    CommonModule,
    SharedModule,
    BrainsRoutingModule
  ]
})
export class BrainsModule { }
