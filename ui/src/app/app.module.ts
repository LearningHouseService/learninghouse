import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { HTTP_INTERCEPTORS, provideHttpClient, withInterceptorsFromDi } from "@angular/common/http";
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LayoutModule } from './modules/layout/layout.module';
import { AuthInterceptor } from './shared/interceptors/auth.interceptor';

// import ngx-translate and the http loader
import { LocationStrategy } from '@angular/common';
import { MatPaginatorIntl } from '@angular/material/paginator';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { TRANSLATE_HTTP_LOADER_CONFIG, TranslateHttpLoader } from '@ngx-translate/http-loader';
import { TranslateMatPaginatorIntl } from './shared/material/translate-mat-paginator-intl';



@NgModule({ declarations: [
        AppComponent
    ],
    bootstrap: [AppComponent], imports: [BrowserModule,
        TranslateModule.forRoot({
            loader: {
                provide: TranslateLoader,
                useClass: TranslateHttpLoader
            }
        }),
        AppRoutingModule,
        BrowserAnimationsModule,
        LayoutModule], providers: [{
            provide: HTTP_INTERCEPTORS,
            useClass: AuthInterceptor,
            multi: true
        },
        {
            provide: MatPaginatorIntl,
            useClass: TranslateMatPaginatorIntl,
        },
        {
            provide: TRANSLATE_HTTP_LOADER_CONFIG,
            useFactory: (locationStrategy: LocationStrategy) => ({
                prefix: `${locationStrategy.getBaseHref()}assets/i18n/`,
                suffix: '.json'
            }),
            deps: [LocationStrategy]
        },
        provideHttpClient(withInterceptorsFromDi())] })
export class AppModule { }