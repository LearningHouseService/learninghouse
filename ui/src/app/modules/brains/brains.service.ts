import { Injectable } from "@angular/core";
import { APIService } from "src/app/shared/services/api.service";
import { BrainInfoModel } from "./brains.model";
import { Observable, map } from "rxjs";
import { BrainConfigurationModel } from "../configuration/configuration.model";

@Injectable({
    providedIn: 'root'
})
export class BrainsService {

    constructor(private api: APIService) { }

    getBrains(): Observable<BrainInfoModel[]> {
        return this.api.get<{ [key: string]: BrainInfoModel }>('/brains/info')
            .pipe(
                map((result) => {
                    const brains: BrainInfoModel[] = [];
                    for (const brain of Object.values(result)) {
                        brains.push(brain);
                    }
                    return brains;
                })
            )
    }

    getBrainInfo(name: string): Observable<BrainInfoModel> {
        return this.api.get<BrainInfoModel>(`/brain/${name}/info`);
    }

    createBrain(brain: BrainConfigurationModel): Observable<BrainConfigurationModel> {
        return this.api.post<BrainConfigurationModel>('/brain/configuration', brain);
    }

    updateBrain(brain: BrainConfigurationModel): Observable<BrainConfigurationModel> {
        return this.api.put<BrainConfigurationModel>('/brain/' + brain.name + '/configuration', brain);
    }

    deleteBrainConfiguration(brainConfiguration: BrainConfigurationModel): Observable<{ name: string }> {
        return this.api.delete('/brain/' + brainConfiguration.name + '/configuration');
    }

    retrainBrain(brainInfo: BrainInfoModel) {
        return this.api.post<BrainInfoModel>('/brain/' + brainInfo.name + '/training', {});
    }
}