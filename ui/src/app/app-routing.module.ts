import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: "", redirectTo: "/brains/prediction", pathMatch: "full" },
  {
    path: 'auth',
    loadChildren: () => import('./modules/auth/auth.module').then((m) => m.AuthModule)
  },
  {
    path: 'brains',
    loadChildren: () => import('./modules/brains/brains.module').then((m) => m.BrainsModule)
  },
  {
    path: 'configuration',
    loadChildren: () => import('./modules/configuration/configuration.module').then((m) => m.ConfigurationModule)
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
