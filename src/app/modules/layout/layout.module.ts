import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { SharedModule } from 'src/app/shared/shared.module';
import { SidenavComponent } from './components/sidenav/sidenav.component';
import { ToolbarComponent } from './components/toolbar/toolbar.component';
import { LayoutRoutingModule } from './layout.routes';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { InfoDialogComponent } from './components/info-dialog/info-dialog.component';



@NgModule({
  declarations: [
    DashboardComponent,
    SidenavComponent,
    ToolbarComponent,
    InfoDialogComponent
  ],
  imports: [
    CommonModule,
    LayoutRoutingModule,
    RouterModule,
    SharedModule
  ],
  exports: [
    SidenavComponent,
    ToolbarComponent,
    InfoDialogComponent
  ]
})
export class LayoutModule { }
