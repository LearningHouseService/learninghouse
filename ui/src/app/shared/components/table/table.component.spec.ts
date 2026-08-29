import { CommonModule } from '@angular/common';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatDialog } from '@angular/material/dialog';
import { MatTableDataSource } from '@angular/material/table';
import { provideTranslateService, TranslatePipe } from '@ngx-translate/core';
import { of } from 'rxjs';
import { BreakpointService } from '../../services/breakpoint.service';
import { TableActionsService } from '../../services/table-actions.service';

import { TableComponent } from './table.component';

describe('TableComponent', () => {
  let component: TableComponent<{ name: string }>;
  let fixture: ComponentFixture<TableComponent<{ name: string }>>;
  const dialog = jasmine.createSpyObj<MatDialog>('MatDialog', ['open']);
  const breakpoints = { isXSmall$: of(false), isSmall$: of(false) };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        TranslatePipe,
        CommonModule,
      ],
      declarations: [TableComponent],
      providers: [
        provideTranslateService(),
        { provide: MatDialog, useValue: dialog },
        { provide: BreakpointService, useValue: breakpoints },
        TableActionsService
      ],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TableComponent<{ name: string }>);
    component = fixture.componentInstance;
    component.dataSource = new MatTableDataSource<{ name: string }>([{ name: 'sensor' }]);
    component.config = { title: 'components.table.title', columns: [{ attr: 'name', label: 'Name' }] };
    fixture.detectChanges();
  });

  it('should create and derive the display columns, incl. the actions column', () => {
    expect(component).toBeTruthy();
    expect(component.displayColumns).toEqual(['name', 'actions']);
  });
});
