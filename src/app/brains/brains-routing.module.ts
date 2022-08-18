import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { AuthGuard } from "../auth/auth.guard";
import { Role } from "../auth/auth.model";
import { PredictionComponent } from "./prediction/prediction.component";
import { TrainingComponent } from "./training/training.component";

const routes: Routes = [
    {
        path: '',
        children: [
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
            },
        ]
    }];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
})
export class BrainsRoutingModule { }