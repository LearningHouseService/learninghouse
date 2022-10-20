import { FocusMonitor } from '@angular/cdk/a11y';
import { BooleanInput, coerceBooleanProperty } from '@angular/cdk/coercion';
import { Component, ElementRef, Inject, Input, OnDestroy, Optional, QueryList, Self, ViewChildren } from '@angular/core';
import { ControlValueAccessor, FormBuilder, NgControl } from '@angular/forms';
import { MatFormField, MatFormFieldControl, MAT_FORM_FIELD } from '@angular/material/form-field';
import { Subject } from 'rxjs';
import { SelectOption } from '../select/select.component';

@Component({
  selector: 'learninghouse-button-group',
  templateUrl: './button-group.component.html',
  styleUrls: ['./button-group.component.scss'],
  providers: [{ provide: MatFormFieldControl, useExisting: ButtonGroupComponent }],
  host: {
    '[class.group-floating]': 'shouldLabelFloat',
    '[id]': 'id',
  }
})
export class ButtonGroupComponent<T> implements MatFormFieldControl<T>, ControlValueAccessor, OnDestroy {
  static nextId = 0;

  @Input()
  options: SelectOption<T>[] = [];

  control = this._formBuilder.control<T | null>(null);

  stateChanges = new Subject<void>();
  focused = false;
  touched = false;
  controlType = 'learninghouse-button-group';
  id = `learninghouse-button-group-${ButtonGroupComponent.nextId++}`;
  onChange = (_: any) => { };
  onTouched = () => { };

  @ViewChildren('button') buttons!: QueryList<ElementRef>;

  get empty() {
    return !this.control.value;
  }

  get shouldLabelFloat() {
    return true;
  }

  @Input('aria-describedby') userAriaDescribedBy: string = '';

  @Input()
  get placeholder(): string {
    return this._placeholder;
  }
  set placeholder(value: string) {
    this._placeholder = value;
    this.stateChanges.next();
  }
  private _placeholder: string = '';

  @Input()
  get required(): boolean {
    return this._required;
  }
  set required(value: BooleanInput) {
    this._required = coerceBooleanProperty(value);
    this.stateChanges.next();
  }
  private _required = false;

  @Input()
  get disabled(): boolean {
    return this._disabled;
  }
  set disabled(value: BooleanInput) {
    this._disabled = coerceBooleanProperty(value);
    this._disabled ? this.control.disable() : this.control.enable();
    this.stateChanges.next();
  }
  private _disabled = false;

  @Input()
  get value(): T | null {
    if (this.control.valid) {
      return this.control.value;
    }
    return null;
  }
  set value(value: T | null) {
    this.control.setValue(value);
    this.stateChanges.next();
  }

  get errorState(): boolean {
    return this.control.invalid && this.touched;
  }

  constructor(
    private _formBuilder: FormBuilder,
    private _focusMonitor: FocusMonitor,
    private _elementRef: ElementRef<HTMLElement>,
    @Optional() @Inject(MAT_FORM_FIELD) public _formField: MatFormField,
    @Optional() @Self() public ngControl: NgControl,
  ) {
    if (this.ngControl != null) {
      this.ngControl.valueAccessor = this;
    }
  }

  autofilled?: boolean;

  ngOnDestroy() {
    this.stateChanges.complete();
    this._focusMonitor.stopMonitoring(this._elementRef);
  }

  onFocusIn(event: FocusEvent) {
    if (!this.focused) {
      this.focused = true;
      this.stateChanges.next();
    }
  }

  onFocusOut(event: FocusEvent) {
    if (!this._elementRef.nativeElement.contains(event.relatedTarget as Element)) {
      this.touched = true;
      this.focused = false;
      this.onTouched();
      this.stateChanges.next();
    }
  }

  setDescribedByIds(ids: string[]) {
    const controlElement = this._elementRef.nativeElement.querySelector(
      '.button-group-element',
    )!;
    if (controlElement) {
      controlElement.setAttribute('aria-describedby', ids.join(' '));
    }
  }

  onContainerClick() {
    if (!this._disabled) {
      this._focusMonitor.focusVia(this.buttons.first, 'program');
      this.onTouched();
    }
  }

  writeValue(value: T | null): void {
    this.value = value;
  }

  registerOnChange(fn: any): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: any): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.disabled = isDisabled;
  }

}