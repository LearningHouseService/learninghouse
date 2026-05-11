import { NO_ERRORS_SCHEMA } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { MatIconRegistry } from '@angular/material/icon';
import { DomSanitizer } from '@angular/platform-browser';
import { RouterTestingModule } from '@angular/router/testing';
import { TranslateModule } from '@ngx-translate/core';
import { AppComponent } from './app.component';
import { AuthService } from './modules/auth/auth.service';

describe('AppComponent', () => {
  const authService = jasmine.createSpyObj<AuthService>('AuthService', ['restoreSession']);
  const matIconRegistry = jasmine.createSpyObj<MatIconRegistry>('MatIconRegistry', ['addSvgIcon']);

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        RouterTestingModule,
        TranslateModule.forRoot()
      ],
      declarations: [
        AppComponent
      ],
      providers: [
        { provide: AuthService, useValue: authService },
        { provide: MatIconRegistry, useValue: matIconRegistry },
        {
          provide: DomSanitizer, useValue: {
            bypassSecurityTrustResourceUrl: (value: string) => value
          }
        }
      ],
      schemas: [NO_ERRORS_SCHEMA]
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it(`should have as title 'learninghouse'`, () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;
    expect(app.title).toEqual('learninghouse');
  });

  it('should render title', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('app-toolbar')).not.toBeNull();
    expect(compiled.querySelector('app-sidenav')).not.toBeNull();
  });
});
