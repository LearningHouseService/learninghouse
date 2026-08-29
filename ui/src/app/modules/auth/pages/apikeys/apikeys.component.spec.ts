import { CommonModule } from '@angular/common';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatDialog } from '@angular/material/dialog';
import { MatSortModule } from '@angular/material/sort';
import { provideTranslateService, TranslatePipe } from '@ngx-translate/core';
import { of } from 'rxjs';
import { TableActionsService } from 'src/app/shared/services/table-actions.service';
import { AuthService } from '../../auth.service';

import { APIKeysComponent } from './apikeys.component';

describe('APIKeysComponent', () => {
  let component: APIKeysComponent;
  let fixture: ComponentFixture<APIKeysComponent>;
  const authService = {
    getAPIKeys: jasmine.createSpy('getAPIKeys').and.returnValue(of([])),
    deleteAPIKey: jasmine.createSpy('deleteAPIKey').and.returnValue(of('ci'))
  };
  const dialog = jasmine.createSpyObj<MatDialog>('MatDialog', ['open']);

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        TranslatePipe,
        CommonModule,
        MatSortModule,
      ],
      declarations: [APIKeysComponent],
      providers: [
        provideTranslateService(),
        { provide: MatDialog, useValue: dialog },
        { provide: AuthService, useValue: authService },
        TableActionsService
      ],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();

    fixture = TestBed.createComponent(APIKeysComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create and load the API keys', () => {
    expect(component).toBeTruthy();
    expect(authService.getAPIKeys).toHaveBeenCalled();
  });
});
