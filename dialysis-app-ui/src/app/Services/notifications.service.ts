import {Injectable} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {Observable, firstValueFrom} from 'rxjs';
import {environment} from "../../environments/environment";
import {AuthService} from './authentication.service';
import {ProviderService} from './provider.service';

@Injectable({
    providedIn: 'root'
})
export class NotificationsService {
    private API_BASE_URL = environment.apiUrl;
    private apiBaseUrl = `${this.API_BASE_URL}/analytics`;

    constructor(
        private http: HttpClient,
        private authService: AuthService,
        private providerService: ProviderService
    ) {
    }

    /** Fetch notifications for the logged-in user or the selected user if the role is provider */
    async getNotifications(): Promise<Observable<any>> {
        const token = localStorage.getItem('token');
        const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
        let userId: number | undefined;

        if (this.authService.getUserRole() === 'provider') {
            // Get the currently selected user from the ProviderService
            const selectedPatient = await firstValueFrom(this.providerService.getSelectedPatient());
            if (selectedPatient) {
                userId = selectedPatient.id;
            }
        } else {
            // may want to do something else here
            userId = this.authService.getUserID() ?? undefined;
        }
        if (!userId) {
            throw new Error('No user selected or logged in. Please select a user to fetch notifications.');
        }
        const url = `${this.apiBaseUrl}/notifications?user_id=${userId}`;
        return this.http.get(url, {headers});
    }

    /** Update notifications for the logged-in user or a specific user */
    updateNotifications(notifications: any, userId?: number): Observable<any> {
        const token = localStorage.getItem('token'); // Retrieve the token from localStorage
        const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
        const url = userId ? `${this.apiBaseUrl}/notifications?user_id=${userId}` : `${this.apiBaseUrl}/notifications`;
        return this.http.put(url, notifications, {headers});
    }
}