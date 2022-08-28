import { Injectable } from '@angular/core';
import { VERSION } from 'src/environments/version';

@Injectable({
  providedIn: 'root'
})
export class AppService {
  get_version(): string {
    return VERSION.semverString;
  }
}
