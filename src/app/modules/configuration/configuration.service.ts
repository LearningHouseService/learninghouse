import { Injectable } from "@angular/core";
import { map, Observable } from "rxjs";
import { Sensor, SensorType } from "src/app/shared/models/configuration.model";
import { APIService } from "src/app/shared/services/api.service";

@Injectable({
    providedIn: 'root'
})
export class ConfigurationService {

    constructor(private api: APIService) { }

    getSensors(): Observable<Sensor[]> {
        return this.api.get<{ [key: string]: SensorType }>('/sensors')
            .pipe(
                map((result) => {
                    const sensors: Sensor[] = [];
                    for (const [name, typed] of Object.entries(result)) {
                        sensors.push({ name: name, typed: typed })
                    }
                    return sensors;
                })
            )
    }
}