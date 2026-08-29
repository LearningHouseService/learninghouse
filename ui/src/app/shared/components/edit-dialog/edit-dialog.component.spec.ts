import { CommonModule } from '@angular/common';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormGroup, ReactiveFormsModule } from '@angular/forms';
import { provideTranslateService, TranslatePipe } from '@ngx-translate/core';
import { EditDialogActionsService } from '../../services/edit-dialog-actions.service';

import { EditDialogComponent } from './edit-dialog.component';

describe('EditDialogComponent', () => {
  let component: EditDialogComponent;
  let fixture: ComponentFixture<EditDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        TranslatePipe,
        CommonModule,
        ReactiveFormsModule,
      ],
      declarations: [EditDialogComponent],
      providers: [
        provideTranslateService(),
        EditDialogActionsService
      ],
      schemas: [NO_ERRORS_SCHEMA]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EditDialogComponent);
    component = fixture.componentInstance;
    component.form = new FormGroup({});
    component.config = { title: 'components.editdialog.title' };
    fixture.detectChanges();
  });

  it('should create and default the response config to an empty object', () => {
    expect(component).toBeTruthy();
    expect(component.config.responseConfig).toEqual({});
  });
});
