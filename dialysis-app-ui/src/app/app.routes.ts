import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
    {
        path: '',
        redirectTo: 'login',
        pathMatch: 'full'
    },
    {
        path: 'login',
        loadComponent: () => import('./Pages/login/login.component').then(m => m.LoginComponent)
    },
    {
        path: 'signup',
        loadComponent: () => import('./Pages/signup/signup.component').then(m => m.SignupComponent)
    },
    {
        path: 'provider-dashboard',
        canActivate: [authGuard('provider')],
        loadComponent: () => import('./Pages/provider-portal/provider-portal.component').then(m => m.ProviderPortalComponent),
    },
    {
        path: 'patient-dashboard',
        canActivate: [authGuard('patient')],
        loadComponent: () => import('./Pages/patient-portal/patient-portal.component').then(m => m.PatientPortalComponent),
    },
    {
        path: 'unauthorized',
        loadComponent: () => import('./Pages/unauthorized/unauthorized.component').then(m => m.UnauthorizedComponent)
    }
];