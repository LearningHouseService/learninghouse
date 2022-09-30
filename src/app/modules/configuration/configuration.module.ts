import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BrainsComponent } from './pages/brains/brains.component';
import { SharedModule } from 'src/app/shared/shared.module';
import { ConfigurationRoutingModule } from './configuration.routes';
import { SensorsComponent } from './pages/sensors/sensors.component';
import { AddEditSensorDialogComponent } from './pages/sensors/add-edit-sensor-dialog/add-edit-sensor-dialog.component';



@NgModule({
  declarations: [
    BrainsComponent,
    SensorsComponent,
    AddEditSensorDialogComponent
  ],
  imports: [
    CommonModule,
    SharedModule,
    ConfigurationRoutingModule
  ]
})
export class ConfigurationModule { }
