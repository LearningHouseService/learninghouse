import { Injectable, VERSION as CORE_VERSION } from '@angular/core';
import { VERSION as APP_VERSION } from 'src/environments/version';

@Injectable({
  providedIn: 'root'
})
export class AppService {
  get_app_version(): string | null {
    return APP_VERSION.semverString;
  }

  get_angular_version(): string {
    return CORE_VERSION.full
  }
}
