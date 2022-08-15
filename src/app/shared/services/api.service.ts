import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class APIService {
  private endpoint_host: string = 'http://localhost:5000/api'

  constructor(private httpClient: HttpClient) { }

  post(endpoint: string, payload: any) {
    return this.httpClient.post(this.endpoint_host + endpoint, payload);
  }
}
