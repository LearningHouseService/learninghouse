import { CommonModule } from '@angular/common';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { BehaviorSubject } from 'rxjs';
import { AuthService } from 'src/app/modules/auth/auth.service';
import { BreakpointService } from 'src/app/shared/services/breakpoint.service';
import { SidenavService } from './sidenav.service';

import { SidenavComponent } from './sidenav.component';

describe('SidenavComponent', () => {
  let component: SidenavComponent;
  let fixture: ComponentFixture<SidenavComponent>;
  const sidenavService = {
    isOpened$: new BehaviorSubject(false),
    toggleNavigation: jasmine.createSpy('toggleNavigation')
  };
  const authService = {
    role$: new BehaviorSubject(null),
    logout: jasmine.createSpy('logout')
  };
  const breakpoints = { isSmall$: new BehaviorSubject(false) };
  const router = jasmine.createSpyObj<Router>('Router', ['navigate']);

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        CommonModule,
        TranslateModule.forRoot()
      ],
      declarations: [SidenavComponent],
      providers: [
        { provide: SidenavService, useValue: sidenavService },
        { provide: AuthService, useValue: authService },
        { provide: BreakpointService, useValue: breakpoints },
        { provide: Router, useValue: router }
      ],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SidenavComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
