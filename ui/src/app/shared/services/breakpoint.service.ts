import { Injectable } from '@angular/core';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { distinctUntilChanged, map } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class BreakpointService {

    readonly isXSmall$ = this.breakpointObserver
        .observe([Breakpoints.XSmall])
        .pipe(
            map((result) => result.matches),
            distinctUntilChanged()
        )

    readonly isSmall$ = this.breakpointObserver
        .observe([Breakpoints.XSmall, Breakpoints.Small])
        .pipe(
            map((result) => result.matches),
            distinctUntilChanged()
        )

    constructor(private breakpointObserver: BreakpointObserver) { }

}