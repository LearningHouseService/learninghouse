import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { SidenavComponent } from './sidenav/sidenav.component';
import { ToolbarComponent } from './toolbar/toolbar.component';



@NgModule({
  declarations: [SidenavComponent, ToolbarComponent],
  imports: [
    CommonModule
  ],
  exports: [
    SidenavComponent,
    ToolbarComponent
  ]
})
export class LayoutModule { }
