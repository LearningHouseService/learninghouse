import { NgModule, inject } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { AuthGuard } from "../../shared/guards/auth.guard";
import { Role } from "../auth/auth.model";
import { SensorsComponent } from "./pages/sensors/sensors.component";

const routes: Routes = [
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