import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { AuthGuard } from "src/app/shared/guards/auth.guard";
import { Role } from "src/app/shared/models/auth.model";
import { APIKeysComponent } from "./pages/apikeys/apikeys.component";
import { ChangePasswordComponent } from "./pages/change-password/change-password.component";
import { LoginComponent } from "./pages/login/login.component";

const routes: Routes = [
    {
        path: '',
        component: LoginComponent

    },
    {
        path: 'apikeys',
        component: APIKeysComponent,
        canActivate: [AuthGuard],
        data: { minimumRole: Role.ADMIN }
    },
    {
        path: 'change_password',
        component: ChangePasswordComponent,
        canActivate: [AuthGuard],
        data: { minimumRole: Role.ADMIN }
    }
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
})
export class AuthRoutingModule { }