import { CommonModule } from '@angular/common';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatDialog } from '@angular/material/dialog';
import { MatSortModule } from '@angular/material/sort';
import { Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { BehaviorSubject, of } from 'rxjs';
import { Role } from 'src/app/modules/auth/auth.model';
import { AuthService } from 'src/app/modules/auth/auth.service';
import { TableActionsService } from 'src/app/shared/services/table-actions.service';
import { BrainsService } from '../../brains.service';

import { BrainsComponent } from './brains.component';

describe('BrainsComponent', () => {
  let component: BrainsComponent;
  let fixture: ComponentFixture<BrainsComponent>;
  const brainsService = {
    getBrains: jasmine.createSpy('getBrains').and.returnValue(of([])),
    deleteBrainConfiguration: jasmine.createSpy('deleteBrainConfiguration').and.returnValue(of({ name: 'x' })),
    retrainBrain: jasmine.createSpy('retrainBrain').and.returnValue(of({}))
  };
  const authService = { role$: new BehaviorSubject<Role | null>(Role.ADMIN) };
  const dialog = jasmine.createSpyObj<MatDialog>('MatDialog', ['open']);
  const router = jasmine.createSpyObj<Router>('Router', ['navigate']);

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        CommonModule,
        MatSortModule,
        TranslateModule.forRoot()
      ],
      declarations: [BrainsComponent],
      providers: [
        { provide: MatDialog, useValue: dialog },
        { provide: Router, useValue: router },
        { provide: BrainsService, useValue: brainsService },
        { provide: AuthService, useValue: authService },
        TableActionsService
      ],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BrainsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create and load the brains, adding the admin row actions', () => {
    expect(component).toBeTruthy();
    expect(brainsService.getBrains).toHaveBeenCalled();
    expect(component.tableConfig.rowActions?.map((action) => action.id)).toEqual(['retrain', 'edit', 'delete']);
  });
});
