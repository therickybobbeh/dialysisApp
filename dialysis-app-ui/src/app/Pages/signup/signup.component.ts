import {Component} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {UserCreate} from "../../Models/users";
import {Router} from '@angular/router';

// PrimeNG modules
import {InputTextModule} from 'primeng/inputtext';
import {PasswordModule} from 'primeng/password';
import {DropdownModule} from 'primeng/dropdown';
import {InputNumberModule} from 'primeng/inputnumber';
import {ButtonModule} from 'primeng/button';

// Angular modules
import {ReactiveFormsModule} from '@angular/forms';
import {NgIf, NgOptimizedImage} from '@angular/common';
import {AuthService} from "../../Services/authentication.service";

@Component({
    selector: 'app-signup',
    standalone: true,
    imports: [
        ReactiveFormsModule,
        InputTextModule,
        PasswordModule,
        DropdownModule,
        InputNumberModule,
        ButtonModule,
        NgIf
    ],
    templateUrl: './signup.component.html',
    styleUrls: ['./signup.component.scss']
})
export class SignupComponent {
    registerForm: FormGroup;
    submitted = false;

    sexes = [
        {label: 'Male', value: 'male'},
        {label: 'Female', value: 'female'}
    ];

    constructor(
        private fb: FormBuilder,
        private authenticationService: AuthService,
        private router: Router
    ) {
        this.registerForm = this.fb.group({
            name: ['', Validators.required],
            email: ['', [Validators.required, Validators.email]],
            password: ['', [Validators.required, Validators.minLength(6)]],
            role: ['patient', Validators.required],
            height: [null, [Validators.required, Validators.min(0)]],
            sex: [null, Validators.required]
        });
    }

    get registerFormControls() {
        return this.registerForm.controls;
    }

    async onSubmit() {
        this.submitted = true;
        if (this.registerForm.invalid) {
            return;
        }
        // Prepare the user object
        const formData = this.registerForm.value;
        const user: UserCreate = {
            ...formData,
            sex: formData.sex?.value, // Convert sex to a string
            role: formData.role || null // Add provider field if not present
        };

        try {
            await this.authenticationService.register(user);
            this.router.navigate(['/login']);
        } catch (err) {
            console.error('Registration failed', err);
            alert('Registration failed. Please try again.');
        }
    }
}