import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddEditBrainDialogComponent } from './add-edit-brain-dialog.component';

describe('AddEditBrainDialogComponent', () => {
  let component: AddEditBrainDialogComponent;
  let fixture: ComponentFixture<AddEditBrainDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AddEditBrainDialogComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddEditBrainDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
