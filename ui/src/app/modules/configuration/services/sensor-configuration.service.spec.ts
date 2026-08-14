import { of } from 'rxjs';
import { SensorConfigurationService } from './sensor-configuration.service';
import { SensorConfigurationModel, SensorType } from '../configuration.model';
import { APIService } from '../../../shared/services/api.service';

function makeSensor(name: string): SensorConfigurationModel {
  return { name, typed: SensorType.NUMERICAL, cycles: 0, calc_sun_position: false };
}

describe('SensorConfigurationService', () => {
  let service: SensorConfigurationService;
  let api: jasmine.SpyObj<APIService>;

  beforeEach(() => {
    api = jasmine.createSpyObj<APIService>('APIService', ['get', 'post', 'put', 'delete']);
    service = new SensorConfigurationService(api);
  });

  it('should fetch all sensor configurations', () => {
    const sensors = [makeSensor('temperature')];
    api.get.and.returnValue(of(sensors));

    let result: SensorConfigurationModel[] = [];
    service.getSensors().subscribe((res) => (result = res));

    expect(api.get).toHaveBeenCalledWith('/sensors/configuration');
    expect(result).toBe(sensors);
  });

  it('should create a sensor with its full payload', () => {
    const sensor = makeSensor('temperature');
    api.post.and.returnValue(of(sensor));

    service.createSensor(sensor).subscribe();

    expect(api.post).toHaveBeenCalledWith('/sensor/configuration', sensor);
  });

  it('should update a sensor by name, embedding the name in the URL', () => {
    const sensor = makeSensor('temperature');
    api.put.and.returnValue(of(sensor));

    service.updateSensor(sensor).subscribe();

    expect(api.put).toHaveBeenCalledWith('/sensor/temperature/configuration', sensor);
  });

  it('should delete a sensor by name', () => {
    const sensor = makeSensor('temperature');
    api.delete.and.returnValue(of({ name: 'temperature' }));

    service.deleteSensor(sensor).subscribe();

    expect(api.delete).toHaveBeenCalledWith('/sensor/temperature/configuration');
  });
});
