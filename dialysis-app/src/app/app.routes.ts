import { Routes } from '@angular/router';
import {LoginComponent} from './Pages/login/login.component';
import {SignupComponent} from './Pages/signup/signup.component';
import {ProviderPortalComponent} from './Pages/provider-portal/provider-portal.component';
import {PatientPortalComponent} from './Pages/patient-portal/patient-portal.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'signup', component: SignupComponent },
  { path: 'provider-portal', component: ProviderPortalComponent },
  { path: 'patient-portal', component: PatientPortalComponent },
  { path: '', redirectTo: 'login', pathMatch: 'full' },
];
