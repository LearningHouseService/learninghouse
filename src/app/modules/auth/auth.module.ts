import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';

import { RouterModule } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { AuthRoutingModule } from './auth.routes';
import { LoginComponent } from './pages/login/login.component';
import { ChangePasswordComponent } from './pages/change-password/change-password.component';
import { APIKeysComponent } from './pages/apikeys/apikeys.component';
import { AddAPIKeyDialogComponent } from './pages/apikeys/add-apikey-dialog/add-apikey-dialog.component';




@NgModule({
  declarations: [
    LoginComponent,
    ChangePasswordComponent,
    APIKeysComponent,
    AddAPIKeyDialogComponent
  ],
  imports: [
    CommonModule,
    SharedModule,
    AuthRoutingModule
  ]
})
export class AuthModule { }
