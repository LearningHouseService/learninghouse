import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { HttpClient, HTTP_INTERCEPTORS, provideHttpClient, withInterceptorsFromDi } from "@angular/common/http";
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LayoutModule } from './modules/layout/layout.module';
import { AuthInterceptor } from './shared/interceptors/auth.interceptor';

// import ngx-translate and the http loader
import { LocationStrategy } from '@angular/common';
import { MatPaginatorIntl } from '@angular/material/paginator';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';
import { TranslateMatPaginatorIntl } from './shared/material/translate-mat-paginator-intl';



@NgModule({ declarations: [
        AppComponent
    ],
    bootstrap: [AppComponent], imports: [BrowserModule,
        TranslateModule.forRoot({
            loader: {
                provide: TranslateLoader,
                useFactory: HttpLoaderFactory,
                deps: [HttpClient, LocationStrategy]
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
        }, provideHttpClient(withInterceptorsFromDi())] })
export class AppModule { }

export function HttpLoaderFactory(http: HttpClient, locationStrategy: LocationStrategy): TranslateHttpLoader {
  const loader = new TranslateHttpLoader(http);
  loader.prefix = `${locationStrategy.getBaseHref()}assets/i18n/`;
  return loader;
}