import { Component, EventEmitter, Input, Output } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { EditDialogActionsService } from '../../services/edit-dialog-actions.service';
import { FormResponseConfig } from '../form-response/form-response.component';

export class SubmitButtonType {
  static readonly SAVE = new SubmitButtonType('save', 'common.buttons.save');

  static readonly ADD = new SubmitButtonType('add', 'components.editdialog.buttons.add');

  static readonly EDIT = new SubmitButtonType('edit', 'components.editdialog.buttons.edit');

  private constructor(public readonly icon: string, public readonly label: string) { }

}

export interface EditDialogConfig {
  title: string;
  submitButton$?: BehaviorSubject<SubmitButtonType | null>;
  responseConfig?: FormResponseConfig
}

@Component({
  selector: 'learninghouse-edit-dialog',
  templateUrl: './edit-dialog.component.html',
  styleUrls: ['./edit-dialog.component.scss']
})
export class EditDialogComponent {

  @Input()
  state: string | null = null;

  @Input()
  valid: boolean = false;

  constructor(public actions: EditDialogActionsService) { }

  @Input()
  set config(values: EditDialogConfig) {
    this._config = {
      responseConfig: {},
      ...values
    };
  }

  get config(): EditDialogConfig {
    return this._config;
  }

  private _config = {
    title: ''
  }

}
