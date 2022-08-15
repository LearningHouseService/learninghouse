import { Component } from '@angular/core';
import { NonNullableFormBuilder, FormGroup, Validators, FormControl } from '@angular/forms';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {

  form: FormGroup;

  constructor(private formBuilder: NonNullableFormBuilder) {
    this.form = this.formBuilder.group({
      password: ['', [Validators.required]]
    });
  }

  get password(): FormControl {
    return (<FormControl>this.form.get('password'));
  }

}
