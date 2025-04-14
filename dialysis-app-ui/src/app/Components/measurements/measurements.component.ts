import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { DialysisService } from '../../Services/dialysis.service';
import { AuthService } from '../../Services/authentication.service';
import { DialysisSessionResponse } from '../../Models/dialysis';
import { catchError, combineLatest, of, Subscription, take, map } from 'rxjs';
import { Calendar } from 'primeng/calendar';
import { DropdownModule } from 'primeng/dropdown';
import { Card } from 'primeng/card';
import { InputText } from 'primeng/inputtext';
import { ButtonDirective, ButtonLabel } from 'primeng/button';
import { DialysisTreatmentData } from '../../Models/patientMeasurements';
import { DatePicker } from 'primeng/datepicker';
import { Select } from 'primeng/select';
import { ProviderService } from '../../Services/provider.service';
import { PatientTableCard } from '../../Models/tables';
import { NgClass, NgIf } from '@angular/common';
import { ConfirmationService } from 'primeng/api';
import { ConfirmDialog } from 'primeng/confirmdialog';

@Component({
  selector: 'app-measurements',
  templateUrl: './measurements.component.html',
  styleUrls: ['./measurements.component.scss'],
  providers: [ConfirmationService],
  imports: [
    Calendar,
    DropdownModule,
    ReactiveFormsModule,
    Card,
    InputText,
    ButtonDirective,
    ButtonLabel,
    DatePicker,
    Select,
    NgClass,
    NgIf,
    ConfirmDialog
  ]
})
export class MeasurementsComponent implements OnInit, OnDestroy {
  @Input() selection: 'pre' | 'post' | undefined;
  measurementsTitle = 'Dialysis';
  dialysisData: DialysisTreatmentData;
  sessionTypes = [
    { label: 'Pre', value: 'pre' },
    { label: 'Post', value: 'post' }
  ];
  private currentPatientId = -1;
  private subscriptions = new Subscription();
  private selectedPatient: PatientTableCard | null = null;
  // This flag toggles based on whether old (saved) session data was loaded for editing.
  protected isEditing = false;
  private previousValues: { session_date: string; session_type: string } | null = null;

  constructor(
    private fb: FormBuilder,
    private dialysisService: DialysisService,
    private authService: AuthService,
    private providerService: ProviderService,
    private confirmationService: ConfirmationService
  ) {
    this.dialysisData = new DialysisTreatmentData();
  }

  ngOnInit() {
    // Set default current patient id and patch into the form.
    this.currentPatientId = this.authService.getUserID() ?? -1;
    this.dialysisData.patchValue({ patient_id: this.currentPatientId });
    this.updateControlsState();

    // Listen for changes on session_date and session_type together.
    const sessionDateControl = this.dialysisData.get('session_date');
    const sessionTypeControl = this.dialysisData.get('session_type');
    if (sessionDateControl && sessionTypeControl) {
      this.subscriptions.add(
        combineLatest([
          sessionDateControl.valueChanges,
          sessionTypeControl.valueChanges
        ]).subscribe(() => this.onDateOrTypeChange())
      );
    }

    // Subscribe to selected patient changes (for providers).
    this.subscriptions.add(
      this.providerService.getSelectedPatient().subscribe(patient => {
        this.selectedPatient = patient;
        // Optionally, trigger re-fetching of data if needed when the patient changes.
      })
    );
  }

  ngOnDestroy() {
    this.subscriptions.unsubscribe();
  }

  /**
   * Triggered when the session_date or session_type changes.
   * If these values have changed from previous values, fetch old data.
   */
onDateOrTypeChange(): void {
  const { session_date, session_type } = this.dialysisData.value;
  if (session_date && session_type) {
    const currentDateStr = session_date.toISOString();

    if (
      !this.previousValues ||
      this.previousValues.session_date !== currentDateStr ||
      this.previousValues.session_type !== session_type
    ) {
      this.fetchOldData(session_date, session_type)
        .pipe(take(1))
        .subscribe(filteredSessions => {
          if (filteredSessions?.length > 0) {
            this.dialysisData.patchValue(filteredSessions[0]);
            this.isEditing = true;
          } else {
            this.dialysisData.reset({ patient_id: this.authService.getUserID() ?? -1 });
            this.dialysisData.patchValue({ session_date, session_type });
            this.isEditing = false;
          }
          this.previousValues = { session_date: currentDateStr, session_type };
          this.updateControlsState();
        });
    }
  }
}

  /**
   * Fetches old session records by date and type.
   */
  fetchOldData(selectedDate: Date, type: string) {
    const isoDate = selectedDate.toISOString();
    return this.dialysisService.getDialysisSessions(isoDate, isoDate, undefined, type).pipe(
      take(1),
      map(filteredSessions => {
        // convert string dates to Date objects.
        if (filteredSessions?.length) {
          const session = filteredSessions[0];
          if (session.session_date) {
            session.session_date = new Date(session.session_date) as any;
          }
          if (session.session_duration) {
            const parsedDuration = new Date(session.session_duration);
            session.session_duration = isNaN(parsedDuration.getTime()) ? null : parsedDuration as any;
          }
        }
        return filteredSessions;
      })
    );
  }

  /**
   * Saves the form data based on role.
   */
  saveData(): void {
    const isProvider = this.authService.getUserRole() === 'provider';
    if (isProvider) {
      if (this.selectedPatient) {
        this.savePatientData(this.dialysisData.value);
      } else {
        console.error('No patient selected for provider.');
        alert('Error: No patient selected.');
      }
    } else {
      this.dialysisService.logDialysisSession(this.dialysisData.value)
        .pipe(
          take(1),
          catchError((error: any) => {
            console.error('Error logging dialysis data as patient:', error);
            alert('Something went wrong.');
            return of(null);
          })
        )
        .subscribe((response: any) => {
          if (response) {
            alert('Submission successful.');
            this.dialysisData.reset();
            this.dialysisData = new DialysisTreatmentData();
            console.log('Logged dialysis data as patient:', response);
          } else {
            alert('Submission failed.');
          }
        });
    }
  }

  /**
   * Saves data for a patient via the provider service.
   */
  savePatientData(updatedData: any): void {
    if (this.selectedPatient) {
      this.providerService.logDialysisSessionForPatient(this.selectedPatient.id, updatedData)
        .subscribe({
          next: response => console.log('Patient data saved successfully:', response),
          error: err => {
            console.error('Error saving patient data:', err);
            alert('Error saving data.');
          }
        });
    } else {
      console.error('No patient selected.');
    }
  }

  /**
   * Confirms deletion of the current session.
   */
  confirmDeleteSession(): void {
    this.confirmationService.confirm({
      message: 'Are you sure you want to delete?',
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: () => this.deleteSessionData()
    });
  }

  /**
   * Deletes the current session.
   */
  deleteSessionData(): void {
    const sessionId = this.dialysisData.value.session_id;
    if (!sessionId) {
      console.error('No session id available.');
      return;
    }
    this.dialysisService.deleteDialysisSession(sessionId)
      .pipe(take(1))
      .subscribe({
        next: response => {
          console.log('Session deleted successfully:', response);
          this.dialysisData.reset();
        },
        error: err => console.error('Error deleting session:', err)
      });
  }

  /**
   * Enables or disables controls based on the presence of session_date and session_type.
   */
  updateControlsState(): void {
    const session_date = this.dialysisData.get('session_date')?.value;
    const session_type = this.dialysisData.get('session_type')?.value;
    for (const controlName of Object.keys(this.dialysisData.controls)) {
      if (session_date && session_type) {
        this.dialysisData.get(controlName)?.enable();
      } else if (controlName !== 'session_date' && controlName !== 'session_type') {
        this.dialysisData.get(controlName)?.disable();
      }
    }
  }
}