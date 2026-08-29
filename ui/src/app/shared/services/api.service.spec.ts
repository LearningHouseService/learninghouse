import { provideHttpClient, withXhr } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { environment } from 'src/environments/environment';
import { LearningHouseError, LearningHouseErrorMessage, LearningHouseVersions, ServiceMode } from '../models/api.model';
import { APIService } from './api.service';

describe('APIService', () => {
  let service: APIService;
  let httpMock: HttpTestingController;
  const base = environment.learninghouseApiUrl;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(withXhr()), provideHttpClientTesting()]
    });
    service = TestBed.inject(APIService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should GET against the configured API base URL', () => {
    service.get<{ ok: boolean }>('/mode').subscribe((result) => {
      expect(result).toEqual({ ok: true });
    });

    const req = httpMock.expectOne(base + '/mode');
    expect(req.request.method).toBe('GET');
    req.flush({ ok: true });
  });

  it('should POST with the given payload', () => {
    const payload = { password: 'secret' };
    service.post<{ ok: boolean }>('/auth/token', payload).subscribe();

    const req = httpMock.expectOne(base + '/auth/token');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(payload);
    req.flush({ ok: true });
  });

  it('should PUT with the given payload', () => {
    const payload = { old_password: 'a', new_password: 'b' };
    service.put<boolean>('/auth/password', payload).subscribe();

    const req = httpMock.expectOne(base + '/auth/password');
    expect(req.request.method).toBe('PUT');
    expect(req.request.body).toEqual(payload);
    req.flush(true);
  });

  it('should DELETE against the given endpoint', () => {
    service.delete<boolean>('/auth/apikey/ci').subscribe();

    const req = httpMock.expectOne(base + '/auth/apikey/ci');
    expect(req.request.method).toBe('DELETE');
    req.flush(true);
  });

  it('should forward request options such as headers', () => {
    service.get('/auth/role', { headers: { 'X-LEARNINGHOUSE-API-KEY': 'the-key' } }).subscribe();

    const req = httpMock.expectOne(base + '/auth/role');
    expect(req.request.headers.get('X-LEARNINGHOUSE-API-KEY')).toBe('the-key');
    req.flush('user');
  });

  it('should map a server error into a LearningHouseError carrying its status, key and description', () => {
    const errorMessage: LearningHouseErrorMessage = { error: 'BrainNotFound', description: 'No such brain.' };
    let caught: LearningHouseError | undefined;

    service.get('/brain/unknown/info').subscribe({
      error: (error: LearningHouseError) => (caught = error)
    });

    httpMock.expectOne(base + '/brain/unknown/info').flush(errorMessage, { status: 404, statusText: 'Not Found' });

    expect(caught).toBeInstanceOf(LearningHouseError);
    expect(caught?.status).toBe(404);
    expect(caught?.key).toBe('BrainNotFound');
    expect(caught?.message).toBe('No such brain.');
  });

  it('should map a client-side/network error (status 0) to a fixed key and message', () => {
    let caught: LearningHouseError | undefined;

    service.get('/mode').subscribe({
      error: (error: LearningHouseError) => (caught = error)
    });

    const req = httpMock.expectOne(base + '/mode');
    req.error(new ProgressEvent('error'), { status: 0, statusText: 'Unknown Error' });

    expect(caught?.status).toBe(0);
    expect(caught?.key).toBe('CLIENT_SIDE');
    expect(caught?.message).toBe('Client side or network error occured.');
  });

  describe('update_mode', () => {
    it('should push the fetched mode onto mode$', () => {
      service.update_mode();

      httpMock.expectOne(base + '/mode').flush(ServiceMode.PRODUCTION);

      expect(service.mode$.getValue()).toBe(ServiceMode.PRODUCTION);
    });

    it('should fall back to UNKNOWN when the request fails', () => {
      service.mode$.next(ServiceMode.PRODUCTION);
      service.update_mode();

      httpMock.expectOne(base + '/mode').flush({ error: 'x', description: 'x' }, { status: 500, statusText: 'Server Error' });

      expect(service.mode$.getValue()).toBe(ServiceMode.UNKNOWN);
    });
  });

  describe('versions', () => {
    it('should map the raw version payload into labeled items', () => {
      const versions: LearningHouseVersions = {
        service: '1.0.0',
        fastapi: '0.1',
        pydantic: '2.0',
        uvicorn: '0.1',
        sklearn: '1.8',
        numpy: '2.0',
        pandas: '3.0',
        jwt: '2.0',
        passlib: '1.0',
        loguru: '0.1'
      };
      let result: { label: string; version: string }[] = [];

      service.versions().subscribe((items) => (result = items));

      httpMock.expectOne(base + '/versions').flush(versions);

      expect(result).toEqual([
        { label: 'LearningHouse Service', version: '1.0.0' },
        { label: 'scikit-learn', version: '1.8' },
        { label: 'FastAPI', version: '0.1' },
        { label: 'Uvicorn', version: '0.1' },
        { label: 'Pydantic', version: '2.0' },
        { label: 'PyJWT', version: '2.0' }
      ]);
    });
  });
});
