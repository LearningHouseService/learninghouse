import { Component, OnInit } from '@angular/core';
import { MatIconRegistry } from "@angular/material/icon";
import { DomSanitizer } from "@angular/platform-browser";
import { AuthService } from './modules/auth/auth.service';
import { TranslateService } from "@ngx-translate/core";
import defaultLanguage from "./../assets/i18n/en.json";
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
    private authService: AuthService,
    private translate: TranslateService) {

    this.initializeTranslation();

    this.matIconRegistry.addSvgIcon(
      'learninghouse',
      this.domSanitizer.bypassSecurityTrustResourceUrl("assets/learninghouse_icon.svg")
    );
  }

  private initializeTranslation(): void {
    this.translate.addLangs(['en', 'de']);
    this.translate.setTranslation('en', defaultLanguage);
    this.translate.setDefaultLang('en');
    let currentLanguage = this.translate.getBrowserLang() || 'en';
    if (this.translate.getLangs().includes(currentLanguage)) {
      this.translate.use(currentLanguage);
    } else {
      this.translate.use('en');
    }
  }

  ngOnInit(): void {
    this.authService.restoreSession();
  }
}
