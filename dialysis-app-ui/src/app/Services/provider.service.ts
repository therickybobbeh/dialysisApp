import { Injectable } from '@angular/core';
import { DialysisSessionCreate, DialysisSessionResponse } from "../Models/dialysis";
import { Observable } from "rxjs";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { PatientTableCard } from "../Models/tables";

@Injectable({
  providedIn: 'root'
})
export class ProviderService {
  private API_BASE_URL = 'http://localhost:8004/provider';

  constructor(private http: HttpClient) {}

  /**
   * GET /provider/patients
   * Fetch the list of patients assigned to the provider.
   */
  getProviderPatients(): Observable<PatientTableCard[]> {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    return this.http.get<PatientTableCard[]>(`${this.API_BASE_URL}/patients`, { headers });
  }

  /**
   * GET /provider/patients/{patient_id}/dialysis
   * Fetch dialysis data for a specific patient.
   */
  getPatientDialysisInfo(patientId: number): Observable<DialysisSessionResponse[]> {
    const token = localStorage.getItem('token');
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    return this.http.get<DialysisSessionResponse[]>(
      `${this.API_BASE_URL}/patients/${patientId}/dialysis`,
      { headers }
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
      { headers }
    );
  }
}