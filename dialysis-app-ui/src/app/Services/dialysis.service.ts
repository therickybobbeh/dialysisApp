import {Injectable} from '@angular/core';
import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import {Observable, take} from 'rxjs';
import {DialysisSessionCreate, DialysisSessionResponse} from '../Models/dialysis';
import {ProviderDashboardRow} from '../Models/provider';
import {ProviderService} from "./provider.service";

@Injectable({
    providedIn: 'root'
})
export class DialysisService {
    private API_BASE_URL = 'http://localhost:8004'; // Update with your actual API base URL
    private baseUrl = `${this.API_BASE_URL}/dialysis`;
    private token = localStorage.getItem('token');

    constructor(private http: HttpClient,
                private providerService: ProviderService) {
    }

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
            {headers}
        );
    }

    /**
     * GET /dialysis/sessions
     * Retrieve dialysis sessions for the current patient (requires user.role = "patient")
     * or for a specific patient (requires user.role = "provider").
     * Accepts optional start_date, end_date, and patient_id as query params.
     */
getDialysisSessions(start_date?: string, end_date?: string, patient_id?: number): Observable<DialysisSessionResponse[]> {
    //TODO: lets also allow for the specification of a pre and post or we can make a new endpoint to get 1 session
    const token = localStorage.getItem('token'); // or this.token
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    let params = new HttpParams();

    if (start_date) {
        params = params.set('start_date', start_date);
    }
    if (end_date) {
        params = params.set('end_date', end_date);
    }
    // Check if patient_id is provided; otherwise, use the selected patient from ProviderService
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

    return this.http.get<DialysisSessionResponse[]>(`${this.baseUrl}/sessions`, { headers, params });
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
        return this.http.delete(`${this.baseUrl}/sessions/${sessionId}`);
    }
}