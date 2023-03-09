import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SidenavService {
  isOpened$ = new BehaviorSubject<boolean>(false);

  constructor() {
    const isOpened = JSON.parse(sessionStorage.getItem('sidenav_is_opened') || 'false') === true;
    this.isOpened$.next(isOpened);
  }

  toggleNavigation(): void {
    const nextOpened = !this.isOpened$.getValue()
    this.isOpened$.next(nextOpened);
    sessionStorage.setItem('sidenav_is_opened', JSON.stringify(nextOpened))
  }

}
