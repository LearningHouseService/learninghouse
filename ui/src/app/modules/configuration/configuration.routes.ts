import { NgModule, inject } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { AuthGuard } from "../../shared/guards/auth.guard";
import { Role } from "../../shared/models/auth.model";
import { BrainsComponent } from "./pages/brains/brains.component";
import { SensorsComponent } from "./pages/sensors/sensors.component";

const routes: Routes = [
    {
        path: 'brains',
        component: BrainsComponent,
        canActivate: [() => inject(AuthGuard).checkMinimumRole(Role.ADMIN)]
    },
    {
        path: 'sensors',
        component: SensorsComponent,
        canActivate: [() => inject(AuthGuard).checkMinimumRole(Role.ADMIN)]
    }
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
})
export class ConfigurationRoutingModule { }