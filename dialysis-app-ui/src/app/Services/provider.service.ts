import {Injectable} from '@angular/core';
import {DialysisSessionCreate, DialysisSessionResponse} from "../Models/dialysis";
import {BehaviorSubject, Observable, take} from "rxjs";
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {PatientTableCard} from "../Models/tables";
import {environment} from "../../environments/environment";

@Injectable({
    providedIn: 'root'
})
export class ProviderService {
    private API_BASE_URL = environment.apiUrl + '/provider';
    // private API_BASE_URL = 'http://localhost:8004/provider';
    public selectedPatientSubject$ = new BehaviorSubject<PatientTableCard | null>(null);
    constructor(private http: HttpClient) {
    }

    getSelectedPatient(): Observable<PatientTableCard | null> {
        return this.selectedPatientSubject$.asObservable();
    }

    setSelectedPatient(patient: PatientTableCard | null): void {
        this.selectedPatientSubject$.next(patient);
    }

    /**
     * GET /provider/patients
     * Fetch the list of patients assigned to the provider.
     */
    getProviderPatients(): Observable<PatientTableCard[]> {
        const token = localStorage.getItem('token');
        const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
        return this.http.get<PatientTableCard[]>(`${this.API_BASE_URL}/patients`, {headers});
    }

    /**
     * GET /provider/patients/{patient_id}/dialysis
     * Fetch dialysis data for a specific patient.
     */
    getPatientDialysisInfo(patientId: number): Observable<DialysisSessionResponse[]> {
        const token = localStorage.getItem('token');
        const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

        // Fetch the list of patients to find the selected patient
        this.getProviderPatients().pipe(take(1)).subscribe((patients) => {
            const selectedPatient = patients.find(patient => patient.id === patientId) || null;
            this.setSelectedPatient(selectedPatient);
        });

        return this.http.get<DialysisSessionResponse[]>(
            `${this.API_BASE_URL}/patients/${patientId}/dialysis`,
            {headers}
        );
    }

    /**
     * POST /provider/patients/{patient_id}/dialysis
     * Log a new dialysis session for a specific patient.
     */
    logDialysisSessionForPatient(patientId: number, sessionData: DialysisSessionCreate): Observable<DialysisSessionResponse> {
        const token = localStorage.getItem('token');
        const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
        return this.http.post<DialysisSessionResponse>(
            `${this.API_BASE_URL}/patients/${patientId}/dialysis`,
            sessionData,
            {headers}
        );
    }
}