import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, catchError, Observable, throwError } from 'rxjs';
import { LearningHouseErrorMessage, ServiceMode } from './api.model';

@Injectable({
  providedIn: 'root'
})
export class APIService {
  private endpoint_host: string = 'http://localhost:5000/api'

  mode$ = new BehaviorSubject<ServiceMode | null>(null);

  constructor(private httpClient: HttpClient) { }

  get<T>(endpoint: string): Observable<T> {
    return this.httpClient.get<T>(this.endpoint_host + endpoint)
      .pipe(
        catchError(this.handleError)
      );
  }

  post<T>(endpoint: string, payload: any): Observable<T> {
    return this.httpClient.post<T>(this.endpoint_host + endpoint, payload)
      .pipe(
        catchError(this.handleError)
      );
  }

  put<T>(endpoint: string, payload: any): Observable<T> {
    return this.httpClient.put<T>(this.endpoint_host + endpoint, payload)
      .pipe(
        catchError(this.handleError)
      );
  }

  private handleError(error: HttpErrorResponse) {
    let message = '';
    if (error.status === 0) {
      message = 'Client side or network error occured.';
    } else {
      const learninghouse_error = error.error as LearningHouseErrorMessage;
      message = learninghouse_error.description;
    }

    console.log(message);
    return throwError(() => new Error(message))

  }

  update_mode(): void {
    this.get<ServiceMode>('/mode')
      .subscribe((result) => {
        this.mode$.next(result)
      });
  }

}
