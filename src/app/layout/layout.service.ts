import { BreakpointObserver, Breakpoints, BreakpointState } from '@angular/cdk/layout';
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LayoutService {

  isMobile$ = new BehaviorSubject<boolean>(false);
  isOpened$ = new BehaviorSubject<boolean>(false);
  isExpanded$ = new BehaviorSubject<boolean>(false);


  constructor(public breakpointObserver: BreakpointObserver) {
    this.breakpointObserver
      .observe([Breakpoints.XSmall])
      .subscribe((state: BreakpointState) => {
        this.isMobile$.next(state.matches);
      });
  }

  toggleNavigation(): void {
    this.isOpened$.next(!this.isOpened$.getValue());
  }

}
