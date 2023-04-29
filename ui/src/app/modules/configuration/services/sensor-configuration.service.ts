import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { SensorConfigurationModel } from "src/app/modules/configuration/configuration.model";
import { APIService } from "src/app/shared/services/api.service";

@Injectable({
    providedIn: 'root'
})
export class SensorConfigurationService {

    constructor(private api: APIService) { }

    getSensors(): Observable<SensorConfigurationModel[]> {
        return this.api.get<SensorConfigurationModel[]>('/sensors/configuration');
    }

    createSensor(sensor: SensorConfigurationModel): Observable<SensorConfigurationModel> {
        return this.api.post('/sensor/configuration', sensor);
    }

    updateSensor(sensor: SensorConfigurationModel): Observable<SensorConfigurationModel> {
        return this.api.put('/sensor/' + sensor.name + '/configuration', sensor);
    }

    deleteSensor(sensor: SensorConfigurationModel): Observable<{ name: string }> {
        return this.api.delete('/sensor/' + sensor.name + '/configuration');
    }
}