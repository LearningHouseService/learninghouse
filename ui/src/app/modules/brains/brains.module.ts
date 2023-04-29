import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { SharedModule } from 'src/app/shared/shared.module';
import { BrainsRoutingModule } from './brains.routes';
import { BrainsComponent } from './pages/brains/brains.component';
import { PredictionComponent } from './pages/prediction/prediction.component';
import { TrainingComponent } from './pages/training/training.component';
import { BraininfoComponent } from './components/braininfo/braininfo.component';



@NgModule({
  declarations: [
    BrainsComponent,
    PredictionComponent,
    TrainingComponent,
    BraininfoComponent
  ],
  imports: [
    CommonModule,
    SharedModule,
    BrainsRoutingModule
  ]
})
export class BrainsModule { }
