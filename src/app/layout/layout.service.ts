import { BreakpointObserver, BreakpointState } from '@angular/cdk/layout';
import { EventEmitter, Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LayoutService {

  isMobile: boolean = false;
  mobileChanged = new Subject<boolean>();
  toggleNavigation = new EventEmitter<void>();

  constructor(public breakpointObserver: BreakpointObserver) {
    this.breakpointObserver
      .observe(['(min-width: 600px)'])
      .subscribe((state: BreakpointState) => {
        this.isMobile = state.matches ? false : true
        this.mobileChanged.next(this.isMobile);
      });
  }

}
