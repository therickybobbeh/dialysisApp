import { Component } from '@angular/core';
import {FormsModule} from '@angular/forms';
import {Button} from 'primeng/button';
import {DropdownModule} from 'primeng/dropdown';
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
  email = '';
  password = '';
  loginTypes = [
    { loginType: 'Patient' },
    { loginType: 'Provider' }
  ];
  selectedLoginType = '';

  onSubmit() {
    console.log('Logging in with:', this.email, this.password);
    alert(`Login Attempt: ${this.email}`);
  }
}
