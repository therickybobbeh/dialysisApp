import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService} from "../Services/authentication.service";

/**
 * Auth Guard that protects routes by:
 * - Ensuring the user is authenticated
 * - Checking for token validity
 * - Optionally enforcing user role
 *
 * @param expectedRole Optional role to restrict access (e.g. 'provider', 'patient')
 */
export function authGuard(expectedRole?: string): CanActivateFn {
  return () => {
    const authService = inject(AuthService);
    const router = inject(Router);

    const token = localStorage.getItem('token');

    if (!token || authService.isTokenExpired(token)) {
      console.warn('Blocked: Not logged in or token expired.');
      router.navigate(['/login']);
      return false;
    }

    const decoded = authService.decodeToken(token);
    if (!decoded) {
      console.warn('Blocked: Invalid token payload.');
      router.navigate(['/login']);
      return false;
    }

    const userRole = decoded.role || decoded.user_role;
    if (expectedRole && userRole !== expectedRole) {
      console.warn(`Blocked: Role mismatch. Needed ${expectedRole}, found ${userRole}`);
      router.navigate(['/unauthorized']);
      return false;
    }

    return true;
  };
}