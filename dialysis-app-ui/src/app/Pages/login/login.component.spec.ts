// import { Component } from '@angular/core';
// import { Router } from '@angular/router';
// import { AuthService} from "../../Services/authentication.service";// or path to your AuthService
//
// @Component({
//   selector: 'app-login',
//   templateUrl: './login.component.html',
//   styleUrls: ['./login.component.scss']
// })
// export class LoginComponent {
//   email = '';
//   password = '';
//   selectedLoginType = 'patient'; // default or whichever
//   loading = false;
//
//   // For the select dropdown
//   loginTypes = [
//     { loginType: 'patient' },
//     { loginType: 'provider' },
//     // ...
//   ];
//
//   constructor(
//     private authService: AuthService,
//     private router: Router
//   ) {}
//
//   onSubmit() {
//     this.loading = true;
//     this.authService.login(this.email, this.password)
//       .then(result => {
//         // result = { token, userId, role }
//         this.loading = false;
//         console.log('Login success!', result);
//         // If user is "provider", maybe navigate to a different dashboard:
//         if (result.userRole === 'provider') {
//           this.router.navigate(['/provider-dashboard']);
//         } else {
//           this.router.navigate(['/patient-dashboard']);
//         }
//       })
//       .catch(error => {
//         this.loading = false;
//         console.error('Login failed:', error);
//         alert('Login failed: ' + (error?.message || error));
//       });
//   }
//
//   onForgotPassword() {
//     alert('Forgot Password logic goes here.');
//   }
// }