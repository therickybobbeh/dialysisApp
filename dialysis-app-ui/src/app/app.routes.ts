import { Routes } from '@angular/router';
import {LoginComponent} from './Pages/login/login.component';
import {SignupComponent} from './Pages/signup/signup.component';
import {ProviderPortalComponent} from './Pages/provider-portal/provider-portal.component';
import {PatientPortalComponent} from './Pages/patient-portal/patient-portal.component';
import {SettingsComponent} from "./Pages/settings/settings.component";

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'signup', component: SignupComponent },
  { path: 'provider-portal', component: ProviderPortalComponent },
  { path: 'patient-portal', component: PatientPortalComponent },
  { path: 'settings', component: SettingsComponent },
  { path: '', redirectTo: 'login', pathMatch: 'full' },
];
