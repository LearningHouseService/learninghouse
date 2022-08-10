import { Component, OnDestroy, OnInit } from '@angular/core';
import { Subscription } from 'rxjs';
import { LayoutService } from '../layout.service';

@Component({
  selector: 'app-toolbar',
  templateUrl: './toolbar.component.html',
  styleUrls: ['./toolbar.component.scss']
})
export class ToolbarComponent implements OnInit, OnDestroy {

  isMobile: boolean = false;
  subscriptionMobile?: Subscription;

  constructor(public layoutService: LayoutService) { }

  ngOnInit(): void {
    this.isMobile = this.layoutService.isMobile;
    this.subscriptionMobile = this.layoutService.mobileChanged.subscribe(isMobile => {
      this.isMobile = isMobile;
    });
  }

  ngOnDestroy(): void {
    if (this.subscriptionMobile) {
      this.subscriptionMobile.unsubscribe();
    }
  }
}
