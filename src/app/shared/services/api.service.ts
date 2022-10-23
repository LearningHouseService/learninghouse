import { HttpClient, HttpContext, HttpErrorResponse, HttpHeaders, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, catchError, map, Observable, of, throwError } from 'rxjs';
import { environment } from 'src/environments/environment';
import { LearningHouseErrorMessage, ServiceMode, LearningHouseError, LearningHouseVersions, VersionItem } from '../models/api.model';

type HttpsParamsType = string | number | boolean | ReadonlyArray<string | number | boolean>;

@Injectable({
  providedIn: 'root'
})
export class APIService {

  mode$ = new BehaviorSubject<ServiceMode>(ServiceMode.UNKNOWN);

  constructor(private httpClient: HttpClient) { }

  get<T>(endpoint: string, options?: {
    headers?: HttpHeaders | {
      [header: string]: string | string[];
    };
    context?: HttpContext;
    observe?: 'body';
    params?: HttpParams | {
      [param: string]: HttpsParamsType;
    };
    reportProgress?: boolean;
    responseType?: 'json';
    withCredentials?: boolean;
  }): Observable<T> {
    return this.httpClient.get<T>(environment.learninghouseApiUrl + endpoint, options)
      .pipe(
        catchError(this.handleError)
      );
  }

  post<T>(endpoint: string, payload: any | null, options?: {
    headers?: HttpHeaders | {
      [header: string]: string | string[];
    };
    context?: HttpContext;
    observe?: 'body';
    params?: HttpParams | {
      [param: string]: HttpsParamsType;
    };
    reportProgress?: boolean;
    responseType?: 'json';
    withCredentials?: boolean;
  }): Observable<T> {
    return this.httpClient.post<T>(environment.learninghouseApiUrl + endpoint, payload, options)
      .pipe(
        catchError(this.handleError)
      );
  }

  put<T>(endpoint: string, payload: any | null, options?: {
    headers?: HttpHeaders | {
      [header: string]: string | string[];
    };
    context?: HttpContext;
    observe?: 'body';
    params?: HttpParams | {
      [param: string]: HttpsParamsType;
    };
    reportProgress?: boolean;
    responseType?: 'json';
    withCredentials?: boolean;
  }): Observable<T> {
    return this.httpClient.put<T>(environment.learninghouseApiUrl + endpoint, payload, options)
      .pipe(
        catchError(this.handleError)
      );
  }

  delete<T>(endpoint: string, options?: {
    headers?: HttpHeaders | {
      [header: string]: string | string[];
    };
    context?: HttpContext;
    observe?: 'body';
    params?: HttpParams | {
      [param: string]: HttpsParamsType;
    };
    reportProgress?: boolean;
    responseType?: 'json';
    withCredentials?: boolean;
  }): Observable<T> {
    return this.httpClient.delete<T>(environment.learninghouseApiUrl + endpoint, options)
      .pipe(
        catchError(this.handleError)
      );
  }

  private handleError(error: HttpErrorResponse) {
    let key = '';
    let message = '';
    if (error.status === 0) {
      key = 'CLIENT_SIDE'
      message = 'Client side or network error occured.';
    } else {
      const learninghouse_error = error.error as LearningHouseErrorMessage;
      key = learninghouse_error.error
      message = learninghouse_error.description;
    }

    const lhError = new LearningHouseError(error.status, key, message)

    console.error(lhError);
    return throwError(() => lhError);

  }

  update_mode(): void {
    this.get<ServiceMode>('/mode')
      .pipe(
        map((mode: ServiceMode) => {
          this.mode$.next(mode);
          return mode;
        }),
        catchError(() => {
          this.mode$.next(ServiceMode.UNKNOWN);
          return of(false);
        })
      )
      .subscribe();
  }

  versions(): Observable<VersionItem[]> {
    return this.get<LearningHouseVersions>('/versions')
      .pipe(
        map((versions: LearningHouseVersions) => {
          return [
            { label: 'LearningHouse Service', version: versions.service },
            { label: 'scikit-learn', version: versions.sklearn },
            { label: 'FastAPI', version: versions.fastapi },
            { label: 'Uvicorn', version: versions.uvicorn },
            { label: 'Pydantic', version: versions.pydantic }
          ]
        })
      );
  }

}

