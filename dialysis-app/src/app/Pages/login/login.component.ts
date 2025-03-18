import { Component } from '@angular/core';
import {FormsModule} from '@angular/forms';
import {Button} from 'primeng/button';
import {DropdownModule} from 'primeng/dropdown';
import {NgForOf} from '@angular/common';
import {MessageService} from "primeng/api";
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    FormsModule,
    Button,
    DropdownModule,
    NgForOf
  ],
  providers: [MessageService],
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

  onForgotPassword() {
    alert('Too bad');
  }

  constructor(private router: Router) {
  }

  //TODO: add route guards to prevent unauthorized access to patient and provider portals
  onSubmit() {
    console.log('Logging in with:', this.email, this.password);
    alert(`Login Attempt: ${this.email}`);
    if (this.selectedLoginType === 'Patient')
      this.router.navigate(['/patient-portal']);
    else if (this.selectedLoginType === 'Provider'){
        this.router.navigate(['/provider-portal']);
    }
  }
}
