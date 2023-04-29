import { Injectable } from "@angular/core";
import { ActivatedRouteSnapshot } from "@angular/router";
import { Observable } from "rxjs";
import { BrainInfoModel } from "./brains.model";
import { BrainsService } from "./brains.service";

@Injectable({
    providedIn: 'root'
})
export class BrainInfoResolverService {
    constructor(private brainsService: BrainsService) { }

    getBrainInfo(snapshot: ActivatedRouteSnapshot): Observable<BrainInfoModel> {
        return this.brainsService.getBrainInfo(snapshot.params['name']);
    }
}