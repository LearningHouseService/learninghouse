import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SharedModule } from 'src/app/shared/shared.module';
import { ConfigurationRoutingModule } from './configuration.routes';
import { SensorsComponent } from './pages/sensors/sensors.component';
import { AddEditSensorDialogComponent } from './pages/sensors/add-edit-sensor-dialog/add-edit-sensor-dialog.component';
import { AddEditBrainDialogComponent } from '../brains/pages/brains/add-edit-brain-dialog/add-edit-brain-dialog.component';



@NgModule({
  declarations: [
    SensorsComponent,
    AddEditSensorDialogComponent,
    AddEditBrainDialogComponent
  ],
  imports: [
    CommonModule,
    SharedModule,
    ConfigurationRoutingModule
  ]
})
export class ConfigurationModule { }
