import { Component, OnDestroy, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { LayoutService } from '../layout.service';

@Component({
  selector: 'app-sidenav',
  templateUrl: './sidenav.component.html',
  styleUrls: ['./sidenav.component.scss']
})
export class SidenavComponent implements OnInit, OnDestroy {

  isMobile: boolean = false;
  isOpened: boolean = false;
  isExpanded: boolean = false;

  subscriptionMobile?: Subscription;
  subscriptionToggle?: Subscription;

  constructor(private layoutService: LayoutService) { }

  ngOnInit(): void {
    this.changeMobileNavbarStates(this.layoutService.isMobile);
    this.subscriptionMobile = this.layoutService.mobileChanged.subscribe(
      isMobile => {
        this.changeMobileNavbarStates(isMobile);
      }
    );
    this.subscriptionToggle = this.layoutService.toggleNavigation.subscribe(() => this.toggle())
  }

  changeMobileNavbarStates(isMobile: boolean): void {
    this.isMobile = isMobile
    if (isMobile) {
      this.isOpened = this.isExpanded;
      this.isExpanded = true;
    } else {
      this.isExpanded = this.isOpened;
      this.isOpened = true;
    }
  }

  ngOnDestroy(): void {
    if (this.subscriptionMobile) {
      this.subscriptionMobile.unsubscribe();
    }

    if (this.subscriptionToggle) {
      this.subscriptionToggle.unsubscribe();
    }
  }

  toggle() {
    if (this.isMobile) {
      this.isOpened = !this.isOpened;
    } else {
      this.isExpanded = !this.isExpanded;
    }
  }

}
