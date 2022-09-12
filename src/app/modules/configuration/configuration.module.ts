import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BrainsComponent } from './pages/brains/brains.component';
import { SharedModule } from 'src/app/shared/shared.module';
import { ConfigurationRoutingModule } from './configuration.routes';
import { SensorsComponent } from './pages/sensors/sensors.component';



@NgModule({
  declarations: [
    BrainsComponent,
    SensorsComponent
  ],
  imports: [
    CommonModule,
    SharedModule,
    ConfigurationRoutingModule
  ]
})
export class ConfigurationModule { }
