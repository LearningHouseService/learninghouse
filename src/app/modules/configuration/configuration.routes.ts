import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { AuthGuard } from "../../shared/guards/auth.guard";
import { Role } from "../../shared/models/auth.model";
import { BrainsComponent } from "./pages/brains/brains.component";
import { SensorsComponent } from "./pages/sensors/sensors.component";

const routes: Routes = [
    {
        path: 'brains',
        component: BrainsComponent,
        canActivate: [AuthGuard],
        data: { minimumRole: Role.ADMIN }
    },
    {
        path: 'sensors',
        component: SensorsComponent,
        canActivate: [AuthGuard],
        data: { minimumRole: Role.ADMIN }
    }
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
})
export class ConfigurationRoutingModule { }