import { Component, OnInit } from '@angular/core';
import { MatIconRegistry } from "@angular/material/icon";
import { DomSanitizer } from "@angular/platform-browser";
import { AuthService } from './auth/auth.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'learninghouse';

  constructor(
    private matIconRegistry: MatIconRegistry,
    private domSanitizer: DomSanitizer,
    private authService: AuthService) {
    this.matIconRegistry.addSvgIcon(
      'learninghouse',
      this.domSanitizer.bypassSecurityTrustResourceUrl("../assets/learninghouse_icon.svg")
    );
  }

  ngOnInit(): void {
    this.authService.restoreSession();
  }
}
