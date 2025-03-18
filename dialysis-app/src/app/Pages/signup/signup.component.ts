import { Component } from '@angular/core';
import {Button} from "primeng/button";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {NgForOf} from "@angular/common";

@Component({
  selector: 'app-signup',
    imports: [
        Button,
        FormsModule,
        NgForOf,
        ReactiveFormsModule
    ],
  templateUrl: './signup.component.html',
  styleUrl: './signup.component.scss'
})
export class SignupComponent {
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
