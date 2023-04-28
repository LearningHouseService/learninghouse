import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { SharedModule } from 'src/app/shared/shared.module';
import { BrainsRoutingModule } from './brains.routes';
import { PredictionComponent } from './pages/prediction/prediction.component';
import { TrainingComponent } from './pages/training/training.component';



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
