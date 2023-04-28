import { NgModule, inject } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { AuthGuard } from "../../shared/guards/auth.guard";
import { Role } from "../../shared/models/auth.model";
import { PredictionComponent } from "./pages/prediction/prediction.component";
import { TrainingComponent } from "./pages/training/training.component";

const routes: Routes = [
    {
        path: 'prediction',
        component: PredictionComponent,
        canActivate: [() => inject(AuthGuard).checkMinimumRole(Role.USER)]
    },
    {
        path: 'training',
        component: TrainingComponent,
        canActivate: [() => inject(AuthGuard).checkMinimumRole(Role.TRAINER)]
    }
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
})
export class BrainsRoutingModule { }