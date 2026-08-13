import { of } from 'rxjs';
import { BrainsService } from './brains.service';
import { BrainInfoModel } from './brains.model';
import { BrainConfigurationModel, BrainEstimatorType } from '../configuration/configuration.model';
import { APIService } from '../../shared/services/api.service';

function makeBrainInfo(name: string): BrainInfoModel {
  return {
    name,
    configuration: { name, estimator: { typed: BrainEstimatorType.CLASSIFIER }, test_size: 0.3 },
    features: [],
    training_data_size: 0,
    score: 0,
    trained_at: null,
    versions: {} as any,
    actual_versions: true
  };
}

describe('BrainsService', () => {
  let service: BrainsService;
  let api: jasmine.SpyObj<APIService>;

  beforeEach(() => {
    api = jasmine.createSpyObj<APIService>('APIService', ['get', 'post', 'put', 'delete']);
    service = new BrainsService(api);
  });

  it('should fetch the brains info map and flatten it into an array', () => {
    const darkness = makeBrainInfo('darkness_ha');
    const heating = makeBrainInfo('heating_ha');
    api.get.and.returnValue(of({ darkness_ha: darkness, heating_ha: heating }));

    let result: BrainInfoModel[] = [];
    service.getBrains().subscribe((brains) => (result = brains));

    expect(api.get).toHaveBeenCalledWith('/brains/info');
    expect(result).toEqual([darkness, heating]);
  });

  it('should fetch a single brain info by name', () => {
    const info = makeBrainInfo('darkness_ha');
    api.get.and.returnValue(of(info));

    service.getBrainInfo('darkness_ha').subscribe();

    expect(api.get).toHaveBeenCalledWith('/brain/darkness_ha/info');
  });

  it('should create a brain via its configuration', () => {
    const config: BrainConfigurationModel = { name: 'new_brain', estimator: { typed: BrainEstimatorType.REGRESSOR }, test_size: 0.2 };
    api.post.and.returnValue(of(config));

    service.createBrain(config).subscribe();

    expect(api.post).toHaveBeenCalledWith('/brain/configuration', config);
  });

  it('should update a brain by name, embedding the name in the URL', () => {
    const config: BrainConfigurationModel = { name: 'darkness_ha', estimator: { typed: BrainEstimatorType.CLASSIFIER }, test_size: 0.3 };
    api.put.and.returnValue(of(config));

    service.updateBrain(config).subscribe();

    expect(api.put).toHaveBeenCalledWith('/brain/darkness_ha/configuration', config);
  });

  it('should delete a brain configuration by name', () => {
    const config: BrainConfigurationModel = { name: 'darkness_ha', estimator: { typed: BrainEstimatorType.CLASSIFIER }, test_size: 0.3 };
    api.delete.and.returnValue(of({ name: 'darkness_ha' }));

    service.deleteBrainConfiguration(config).subscribe();

    expect(api.delete).toHaveBeenCalledWith('/brain/darkness_ha/configuration');
  });

  it('should trigger a retraining for the given brain, with an empty payload', () => {
    const info = makeBrainInfo('darkness_ha');
    api.post.and.returnValue(of(info));

    service.retrainBrain(info);

    expect(api.post).toHaveBeenCalledWith('/brain/darkness_ha/training', {});
  });
});
