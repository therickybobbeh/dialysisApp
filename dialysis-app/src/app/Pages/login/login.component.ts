import { Component } from '@angular/core';
import {FormsModule} from '@angular/forms';
import {Button, ButtonDirective} from 'primeng/button';
import {InputText} from 'primeng/inputtext';
import {DropdownModule} from 'primeng/dropdown';
import {Select} from 'primeng/select';
import {NgForOf} from '@angular/common';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    FormsModule,


    Button,
    DropdownModule,

    NgForOf
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  email: string = '';
  password: string = '';
  loginTypes = [
    { loginType: 'Patient' },
    { loginType: 'Provider' }
  ];
  selectedLoginType: string = '';

  onSubmit() {
    console.log('Logging in with:', this.email, this.password);
    alert(`Login Attempt: ${this.email}`);
  }
}
