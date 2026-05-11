import { CommonModule } from '@angular/common';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { BehaviorSubject } from 'rxjs';
import { AuthService } from 'src/app/modules/auth/auth.service';
import { BreakpointService } from 'src/app/shared/services/breakpoint.service';
import { SidenavService } from '../sidenav/sidenav.service';

import { ToolbarComponent } from './toolbar.component';

describe('ToolbarComponent', () => {
  let component: ToolbarComponent;
  let fixture: ComponentFixture<ToolbarComponent>;
  const sidenavService = { toggleNavigation: jasmine.createSpy('toggleNavigation') };
  const authService = {
    refreshTokenExpireDate$: new BehaviorSubject<Date | null>(null),
    logout: jasmine.createSpy('logout'),
    refreshToken: jasmine.createSpy('refreshToken').and.returnValue(null)
  };
  const breakpoints = { isSmall$: new BehaviorSubject(false) };
  const dialog = { open: jasmine.createSpy('open') };
  const router = jasmine.createSpyObj<Router>('Router', ['navigate']);

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        CommonModule,
        TranslateModule.forRoot()
      ],
      declarations: [ToolbarComponent],
      providers: [
        { provide: SidenavService, useValue: sidenavService },
        { provide: AuthService, useValue: authService },
        { provide: BreakpointService, useValue: breakpoints },
        { provide: MatDialog, useValue: dialog },
        { provide: Router, useValue: router }
      ],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ToolbarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
