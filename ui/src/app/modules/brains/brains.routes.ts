import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { AuthGuard } from "../../shared/guards/auth.guard";
import { Role } from "../../shared/models/auth.model";
import { PredictionComponent } from "./pages/prediction/prediction.component";
import { TrainingComponent } from "./pages/training/training.component";

const routes: Routes = [
    {
        path: 'prediction',
        component: PredictionComponent,
        canActivate: [AuthGuard],
        data: { minimumRole: Role.USER }
    },
    {
        path: 'training',
        component: TrainingComponent,
        canActivate: [AuthGuard],
        data: { minimumRole: Role.TRAINER }
    }
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
})
export class BrainsRoutingModule { }