import {Component, Input, OnDestroy, OnInit} from '@angular/core';
import {FormBuilder, ReactiveFormsModule} from '@angular/forms';
import {DialysisService} from '../../Services/dialysis.service';
import {AuthService} from '../../Services/authentication.service';
import {DialysisSessionResponse} from '../../Models/dialysis';
import {catchError, of, Subscription, take} from 'rxjs';
import {Calendar} from "primeng/calendar";
import {DropdownModule} from "primeng/dropdown";
import {Card} from "primeng/card";
import {InputText} from "primeng/inputtext";
import {ButtonDirective, ButtonLabel} from "primeng/button";
import {DialysisTreatmentData} from '../../Models/patientMeasurements';
import {DatePicker} from "primeng/datepicker";
import {Select} from "primeng/select";
import {ProviderService} from "../../Services/provider.service";
import {PatientTableCard} from "../../Models/tables";
import {NgClass, NgIf} from "@angular/common"; // Import the class

@Component({
    selector: 'app-measurements',
    templateUrl: './measurements.component.html',
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
        NgIf
    ],
    styleUrls: ['./measurements.component.scss']
})
export class MeasurementsComponent implements OnInit, OnDestroy {
    @Input() selection: 'pre' | 'post' | undefined;
    allDialysisSessions: DialysisSessionResponse[] = [];
    measurementsTitle = 'Dialysis';
    dialysisData: DialysisTreatmentData;
    sessionTypes = [
        {label: 'Pre', value: 'pre'},
        {label: 'Post', value: 'post'}
    ];
    private currentPatientId = -1;
    private subscription = new Subscription;
    private selectedPatient: PatientTableCard | null = null;
    protected isEditing = false;
    private previousValues: { session_date: string; session_type: string } | null = null;

    constructor(
        private fb: FormBuilder,
        private dialysisService: DialysisService,
        private authService: AuthService,
        private providerService: ProviderService
    ) {
        this.dialysisData = new DialysisTreatmentData();
    }


    ngOnInit() {
        this.currentPatientId = this.authService.getUserID() ?? -1;
        this.dialysisData.patchValue({patient_id: this.currentPatientId});
        this.subscription.add(
            this.providerService.getSelectedPatient().subscribe(patient => {
                this.selectedPatient = patient;
            })
        );
    }

    ngOnDestroy() {
        this.subscription.unsubscribe()
    }


    onDateOrTypeChange(): void {
        this.isEditing = false;
        const {session_date, session_type} = this.dialysisData.value;
        if (session_date && session_type) {
            const currentDateStr = session_date.toISOString();
            if (!this.previousValues ||
                this.previousValues.session_date !== currentDateStr ||
                this.previousValues.session_type !== session_type) {
                this.fetchOldData(session_date, session_type);
            }
            this.previousValues = {session_date: currentDateStr, session_type};
        }
    }

    fetchOldData(selectedDate: Date, type: string): void {
        const isoDate = selectedDate.toISOString();
        this.dialysisService.getDialysisSessions(isoDate, isoDate, undefined, type)
            .pipe(take(1))
            .subscribe(filteredSessions => {
                this.dialysisData.reset();
                if (filteredSessions && filteredSessions.length > 0) {
                    const session = filteredSessions[0];
                    if (session.session_date) {
                        session.session_date = new Date(session.session_date) as any;
                    }
                    if (session.session_duration) {
                        const parsedDuration = new Date(session.session_duration);
                        session.session_duration = isNaN(parsedDuration.getTime()) ? null : parsedDuration as any;
                    }
                    this.dialysisData.patchValue(session);
                    this.isEditing = true;
                }
            });
    }

    saveData() {
        const isProvider = this.authService.getUserRole() === "provider";
        if (isProvider) {
            if (this.selectedPatient) {
                this.savePatientData(this.dialysisData.value);
            } else {
                console.error('No patient selected for provider.');
            }
        } else {
            // patient flow
            this.dialysisService.logDialysisSession(this.dialysisData.value)
                .pipe(
                    take(1),
                    catchError((error: any) => {
                        console.error('Error logging dialysis data as patient:', error);
                        return of(null);
                    })
                )
                .subscribe((response: any) => {
                    if (response) {
                        this.dialysisData.reset();
                        this.dialysisData = new DialysisTreatmentData();
                        console.log('Logged dialysis data as patient:', response);
                    } else {
                        console.log('Failed to log dialysis data as patient.');
                    }
                });
        }
    }

    savePatientData(updatedData: any): void {
        if (this.selectedPatient) {
            this.providerService.logDialysisSessionForPatient(this.selectedPatient.id, updatedData)
                .subscribe({
                    next: (response: any) => {
                        console.log('Patient data saved successfully:', response);
                    },
                    error: (err: any) => {
                        console.error('Error saving patient data:', err);
                    }
                });
        } else {
            console.error('No patient selected.');
        }
    }

    deleteSessionData(): void {
        const sessionId = this.dialysisData.value.session_id;
        if (!sessionId) {
            console.error("No session id available.");
            return;
        }
        this.dialysisService.deleteDialysisSession(sessionId)
            .pipe(take(1))
            .subscribe({
                next: (response: any) => {
                    console.log("Session deleted successfully:", response);
                    this.fetchOldData(this.dialysisData.value.session_date, this.dialysisData.value.session_type);
                },
                error: (err: any) => {
                    console.error("Error deleting session:", err);
                }
            });
    }
}