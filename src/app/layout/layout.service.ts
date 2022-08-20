import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LayoutService {
  isOpened$ = new BehaviorSubject<boolean>(false);

  toggleNavigation(): void {
    this.isOpened$.next(!this.isOpened$.getValue());
  }

}
