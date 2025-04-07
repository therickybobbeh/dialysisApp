import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {Router} from '@angular/router';

@Injectable({providedIn: 'root'})
export class AuthService {
    //TODO: add to the env
    private apiBaseUrl = 'http://localhost:8004';

    constructor(private http: HttpClient, private router: Router) {
    }

    /** Login: obtains token and user info. */
    async login(email: string, password: string) {
        const body = new HttpParams()
            .set('username', email)
            .set('password', password);

        try {
            const response = await this.http.post<{ access_token: string }>(
                `${this.apiBaseUrl}/auth/token`,
                body,
                {headers: {'Content-Type': 'application/x-www-form-urlencoded'}}
            ).toPromise();

            if (!response || !response.access_token) {
                throw new Error('No token received');
            }

            const token = response.access_token;

            // decode JWT
            const decoded = this.decodeToken(token);
            const userId = decoded.user_id || decoded.sub;
            const userRole = decoded.role;

            if (!userId) {
                console.error('No user_id in JWT payload!');
                throw new Error('Invalid token: Missing user_id');
            }

            localStorage.setItem('token', token);
            localStorage.setItem('user_id', String(userId));
            localStorage.setItem('user_role', userRole);

            console.log('Login successful:', {userId, userRole});
            return {token, userId, userRole};
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    }

    /** Refresh token logic. */
    async refreshToken(): Promise<string | null> {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            console.warn('No refresh token found, redirecting to login.');
            this.logout();
            return null;
        }

        try {
            const response = await this.http.post<{
                access_token: string;
                refresh_token: string;
            }>(`${this.apiBaseUrl}/auth/refresh`, {refreshToken}).toPromise();

            localStorage.setItem('token', response!.access_token);
            localStorage.setItem('refresh_token', response!.refresh_token);
            console.log('Access token refreshed!');
            return response!.access_token;
        } catch (err) {
            console.error('Refresh token expired/invalid. Logging out...');
            this.logout();
            return null;
        }
    }

    /** Logout function */
    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_role');
        localStorage.removeItem('user_id');
        this.router.navigate(['/login']);
    }

    /** Return whether user is authenticated */
    isAuthenticated(): boolean {
        return !!localStorage.getItem('token');
    }

    /** Get user role */
    getUserRole(): string {
        return localStorage.getItem('user_role') || 'guest';
    }

    getUserID(): string {
        return localStorage.getItem('user_id') || '';
    }

    /** Decode token to check expiry, user_id, etc. */
    decodeToken(token: string): any {
        try {
            const payload = token.split('.')[1];
            return JSON.parse(atob(payload));
        } catch (error) {
            return null;
        }
    }

    /** Check if token is expired */
    isTokenExpired(token: string): boolean {
        const decoded = this.decodeToken(token);
        if (!decoded || !decoded.exp) return true;
        return decoded.exp * 1000 < Date.now();
    }
}