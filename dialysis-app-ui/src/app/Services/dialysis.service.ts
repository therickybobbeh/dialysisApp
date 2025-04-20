import {Injectable} from '@angular/core';
import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import {map, Observable, take, tap} from 'rxjs';
import {DialysisSessionCreate, DialysisSessionResponse} from '../Models/dialysis';
import {ProviderService} from "./provider.service";
import {environment} from "../../environments/environment";
import {NotificationsService} from "./notifications.service";

@Injectable({
    providedIn: 'root'
})
export class DialysisService {
    private API_BASE_URL = environment.apiUrl
    private baseUrl = `${this.API_BASE_URL}/dialysis`;
    private token = localStorage.getItem('token');

    constructor(private http: HttpClient,
                private providerService: ProviderService,
                private notificationsService: NotificationsService) {
    }

    /**
     * POST /dialysis/sessions
     * Log a new dialysis session.
     */
    logDialysisSession(sessionData: DialysisSessionCreate): Observable<DialysisSessionResponse> {
        const token = localStorage.getItem('token');
        const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
        return this.http.post<DialysisSessionResponse>(
            `${this.baseUrl}/sessions`,
            sessionData,
            {headers}
        );
    }




    /**
     * GET /dialysis/sessions
     * Retrieve dialysis sessions for the current patient (requires user.role = "patient")
     * or for a specific patient (requires user.role = "provider").
     * Accepts optional start_date, end_date, patient_id, and session_type as query params.
     */
    getDialysisSessions(
        start_date?: string,
        end_date?: string,
        patient_id?: number,
        session_type?: string
    ): Observable<DialysisSessionResponse[]> {
        const token = localStorage.getItem('token');
        const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
        let params = new HttpParams();

        if (start_date) {
            params = params.set('start_date', start_date);
        }
        if (end_date) {
            params = params.set('end_date', end_date);
        }
        if (!patient_id) {
            const selectedPatient = this.providerService.getSelectedPatient();
            selectedPatient.pipe(take(1)).subscribe((patient) => {
                if (patient) {
                    params = params.set('patient_id', patient.id.toString());
                }
            });
        } else {
            params = params.set('patient_id', patient_id.toString());
        }

        return this.http.get<DialysisSessionResponse[]>(`${this.baseUrl}/sessions`, {headers, params})
            .pipe(
                map(sessions => {
                    if (session_type) {
                        return sessions.filter(session => session.session_type === session_type);
                    }
                    return sessions;
                }),
                tap(() => this.notificationsService.triggerReload())
            );
    }

    /**
     * PUT /dialysis/sessions/{session_id}
     * Update a dialysis session (patient's own session).
     */
    updateDialysisSession(sessionId: number, sessionData: DialysisSessionCreate): Observable<DialysisSessionResponse> {
        return this.http.put<DialysisSessionResponse>(`${this.baseUrl}/sessions/${sessionId}`, sessionData);
    }


    /**
     * DELETE /dialysis/sessions/{session_id}
     * Patient can delete their own session.
     */
    deleteDialysisSession(sessionId: number): Observable<any> {
        const token = localStorage.getItem('token');
        const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
        return this.http.delete(`${this.baseUrl}/sessions/${sessionId}`, {headers});
    }
}