import { Component, OnInit } from '@angular/core';
import { PatientTableCard } from '../../Models/tables';
import { ProviderService } from '../../Services/provider.service';
import {TableModule} from "primeng/table";

@Component({
  selector: 'app-patient-list',
  templateUrl: './patient-list.component.html',
  imports: [
    TableModule
  ],
  styleUrls: ['./patient-list.component.scss']
})
export class PatientListComponent implements OnInit {
  patients: PatientTableCard[] = [];
  selectedPatient: PatientTableCard | null = null;

  constructor(private providerService: ProviderService) {}

  ngOnInit(): void {
    this.loadPatients();
  }

  loadPatients(): void {
    this.providerService.getProviderPatients().subscribe({
      next: (data) => {
        this.patients = data;
        if (this.patients.length > 0) {
          this.selectPatient(this.patients[0]);
        }
      },
      error: (err) => {
        console.error('Error loading patients:', err);
      }
    });
  }

  selectPatient(patient: PatientTableCard): void {
    this.selectedPatient = patient;
    this.loadPatientData(patient.id);
  }

  loadPatientData(patientId: number): void {
    this.providerService.getPatientDialysisInfo(patientId).subscribe({
      next: (data) => {
        console.log('Loaded patient data:', data);
      },
      error: (err) => {
        console.error('Error loading patient data:', err);
      }
    });
  }

  savePatientData(updatedData: any): void {
    if (this.selectedPatient) {
      this.providerService.logDialysisSessionForPatient(this.selectedPatient.id, updatedData).subscribe({
        next: (response) => {
          console.log('Patient data saved successfully:', response);
        },
        error: (err) => {
          console.error('Error saving patient data:', err);
        }
      });
    }
  }
}