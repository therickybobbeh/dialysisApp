import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DialysisSessionCreate, DialysisSessionResponse } from '../Models/dialysis';
import { ProviderDashboardRow } from '../Models/provider';

@Injectable({
    providedIn: 'root'
})
export class DialysisService {
    private API_BASE_URL = 'http://localhost:8004'; // Update with your actual API base URL
    private baseUrl = `${this.API_BASE_URL}/dialysis`;
    private token = localStorage.getItem('token');

    constructor(private http: HttpClient) {}

    /**
     * POST /dialysis/sessions
     * Log a new dialysis session.
     */
    logDialysisSession(sessionData: DialysisSessionCreate): Observable<DialysisSessionResponse> {
        const token = localStorage.getItem('token'); // or this.token
        const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
        return this.http.post<DialysisSessionResponse>(
            `${this.baseUrl}/sessions`,
            sessionData,
            { headers }
        );
    }

    /**
     * GET /dialysis/sessions
     * Retrieve dialysis sessions for the current patient (requires user.role = "patient").
     * Accepts optional start_date, end_date as query params.
     */
    getDialysisSessions(start_date?: string, end_date?: string): Observable<DialysisSessionResponse[]> {
        let params = new HttpParams();
        if (start_date) {
            params = params.set('start_date', start_date);
        }
        if (end_date) {
            params = params.set('end_date', end_date);
        }

        return this.http.get<DialysisSessionResponse[]>(`${this.baseUrl}/sessions`, { params });
    }

    /**
     * GET /dialysis/provider-dashboard
     * Fetch flagged patients info (requires user.role = "provider").
     * Accepts optional start_date, end_date as query params.
     */
    getProviderDashboard(start_date?: string, end_date?: string): Observable<ProviderDashboardRow[]> {
        let params = new HttpParams();
        if (start_date) {
            params = params.set('start_date', start_date);
        }
        if (end_date) {
            params = params.set('end_date', end_date);
        }

        return this.http.get<ProviderDashboardRow[]>(`${this.baseUrl}/provider-dashboard`, { params });
    }

    /**
     * PUT /dialysis/sessions/{session_id}
     * Update a dialysis session (patient's own session).
     */
    updateDialysisSession(sessionId: number, sessionData: DialysisSessionCreate): Observable<DialysisSessionResponse> {
        return this.http.put<DialysisSessionResponse>(`${this.baseUrl}/sessions/${sessionId}`, sessionData);
    }

    /**
     * GET /dialysis/all-sessions
     * Provider can view all sessions from all patients.
     */
    getAllSessions(): Observable<DialysisSessionResponse[]> {
        const headers = new HttpHeaders().set('Authorization', `Bearer ${this.token}`);
        return this.http.get<DialysisSessionResponse[]>(`${this.baseUrl}/all-sessions`, { headers });
    }

    /**
     * DELETE /dialysis/sessions/{session_id}
     * Patient can delete their own session.
     */
    deleteDialysisSession(sessionId: number): Observable<any> {
        return this.http.delete(`${this.baseUrl}/sessions/${sessionId}`);
    }

    /**
     * GET /dialysis/patient/live-updates
     * Return recent dialysis sessions from the last 5 minutes (requires patient role).
     */
    getPatientLiveUpdates(): Observable<DialysisSessionResponse[] | { message: string }> {
        return this.http.get<DialysisSessionResponse[] | { message: string }>(
            `${this.baseUrl}/patient/live-updates`
        );
    }

    /**
     * GET /dialysis/provider/live-updates
     * Return recent sessions from last 5 minutes for all patients (requires provider role).
     */
    getProviderLiveUpdates(): Observable<DialysisSessionResponse[] | { message: string }> {
        return this.http.get<DialysisSessionResponse[] | { message: string }>(
            `${this.baseUrl}/provider/live-updates`
        );
    }
}