import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'learninghouse-edit-dialog',
  templateUrl: './edit-dialog.component.html',
  styleUrls: ['./edit-dialog.component.scss']
})
export class EditDialogComponent {

  @Input()
  title: string = '';

  @Input()
  success: boolean = false;

  @Input()
  successMessage?: string = 'common.messages.success';

  @Input()
  error: string | null = null;

  @Input()
  errorPrefix?: string;

  @Input()
  valid!: boolean

  @Input()
  add: boolean = false;

  @Output()
  onAdd = new EventEmitter<void>();

  @Input()
  edit: boolean = false;

  @Output()
  onEdit = new EventEmitter<void>();

  @Output()
  onClose = new EventEmitter<void>();

}
