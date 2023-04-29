import { NgModule, inject } from "@angular/core";
import { ActivatedRouteSnapshot, RouterModule, Routes } from "@angular/router";
import { AuthGuard } from "../../shared/guards/auth.guard";
import { Role } from "../auth/auth.model";
import { BrainsComponent } from "./pages/brains/brains.component";
import { PredictionComponent } from "./pages/prediction/prediction.component";
import { TrainingComponent } from "./pages/training/training.component";
import { BrainInfoResolverService } from "./braininfo-resolver.service.ts";

const routes: Routes = [
    {
        path: '',
        pathMatch: 'full',
        component: BrainsComponent,
        canActivate: [() => inject(AuthGuard).checkMinimumRole(Role.USER)]
    },
    {
        path: 'prediction/:name',
        component: PredictionComponent,
        canActivate: [() => inject(AuthGuard).checkMinimumRole(Role.USER)]
    },
    {
        path: 'training/:name',
        component: TrainingComponent,
        canActivate: [() => inject(AuthGuard).checkMinimumRole(Role.TRAINER)],
        resolve: {
            brainInfo: (snapshot: ActivatedRouteSnapshot) => inject(BrainInfoResolverService).getBrainInfo(snapshot)
        }
    }
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule],
    providers: [BrainInfoResolverService]
})
export class BrainsRoutingModule { }