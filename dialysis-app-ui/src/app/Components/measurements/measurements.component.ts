import {ChangeDetectorRef, Component, Input, OnDestroy, OnInit} from '@angular/core';
import {FormBuilder, ReactiveFormsModule} from '@angular/forms';
import {DialysisService} from '../../Services/dialysis.service';
import {AuthService} from '../../Services/authentication.service';
import {catchError, combineLatest, debounceTime, distinctUntilChanged, of, Subscription, take, map} from 'rxjs';
import {Calendar} from 'primeng/calendar';
import {DropdownModule} from 'primeng/dropdown';
import {Card} from 'primeng/card';
import {InputText} from 'primeng/inputtext';
import {ButtonDirective, ButtonLabel} from 'primeng/button';
import {DialysisTreatmentData} from '../../Models/patientMeasurements';
import {DatePicker} from 'primeng/datepicker';
import {Select} from 'primeng/select';
import {ProviderService} from '../../Services/provider.service';
import {PatientTableCard} from '../../Models/tables';
import {NgClass, NgIf} from '@angular/common';
import {ConfirmationService} from 'primeng/api';
import {ConfirmDialog} from 'primeng/confirmdialog';
import {Tooltip} from 'primeng/tooltip';
import {Dialog} from "primeng/dialog";

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
        ConfirmDialog,
        Tooltip,
        Dialog
    ]
})
export class MeasurementsComponent implements OnInit, OnDestroy {
    @Input() selection: 'pre' | 'post' | undefined;
    measurementsTitle = 'Dialysis';
    dialysisData: DialysisTreatmentData;
    sessionTypes = [
        {label: 'Pre', value: 'pre'},
        {label: 'Post', value: 'post'}
    ];
    private currentPatientId = -1;
    private subscriptions = new Subscription();
    private selectedPatient: PatientTableCard | null = null;
    protected isEditing = false;
    private previousValues: { session_date: string; session_type: string } | null = null;
    // Guard flag to avoid processing during programmatic updates
    private updatingForm = false;
    private userId?: number;
    public displayDialog = false;
    public dialogMessage = '';

    constructor(
        private fb: FormBuilder,
        private dialysisService: DialysisService,
        private authService: AuthService,
        private providerService: ProviderService,
        private confirmationService: ConfirmationService,
        private cdRef: ChangeDetectorRef

    ) {
        this.dialysisData = new DialysisTreatmentData();
    }

    ngOnInit() {
        // Existing initialization logic
        const userRole = this.authService.getUserRole();
        if (userRole === 'provider') {
            this.subscriptions.add(
                this.providerService.selectedPatientSubject$.subscribe(selectedPatient => {
                    this.userId = selectedPatient?.id ?? -1;
                    this.currentPatientId = selectedPatient?.id ?? -1;
                    this.dialysisData.reset({patient_id: this.currentPatientId});
                    this.updateControlsState();
                })
            );
        } else {
            this.userId = this.authService.getUserID() ?? -1;
            this.currentPatientId = this.authService.getUserID() ?? -1;
        }
        this.dialysisData.patchValue({patient_id: this.currentPatientId}, {emitEvent: false});
        this.updateControlsState();

        // Existing subscriptions for form controls
        const dateCtrl = this.dialysisData.get('session_date');
        const typeCtrl = this.dialysisData.get('session_type');
        if (dateCtrl && typeCtrl) {
            this.subscriptions.add(
                combineLatest([
                    dateCtrl.valueChanges.pipe(
                        debounceTime(100),
                        distinctUntilChanged((prev, curr) =>
                            prev && curr ? prev.toISOString() === curr.toISOString() : prev === curr
                        )
                    ),
                    typeCtrl.valueChanges.pipe(debounceTime(100), distinctUntilChanged())
                ]).subscribe(([date, type]) => {
                    if (date && type) {
                        this.onDateOrTypeChange();
                    }
                })
            );
        }
    }

    ngOnDestroy() {
        this.subscriptions.unsubscribe();
    }

    /**
     * Called when session_date or session_type change.
     * Uses a guard flag to prevent loops and resets/preserves the chosen date.
     */
    onDateOrTypeChange(): void {
        // Guard against infinite loops with the form
        if (this.updatingForm) {
            return;
        }
        const {session_date, session_type} = this.dialysisData.value;
        if (!session_date || !session_type) {
            return;
        }
        const currentDateStr = session_date.toISOString();

        if (
            this.previousValues &&
            this.previousValues.session_date === currentDateStr &&
            this.previousValues.session_type === session_type
        ) {
            return;
        }
        this.previousValues = {session_date: currentDateStr, session_type};
        this.fetchOldData(session_date, session_type)
            .pipe(take(1))
            .subscribe(filteredSessions => {
                this.updatingForm = true;
                if (filteredSessions?.length > 0) {
                    this.dialysisData.patchValue({
                        ...filteredSessions[0],
                        session_date,
                        session_type
                    }, {emitEvent: false});
                    this.isEditing = true;
                } else {
                    this.dialysisData.reset({patient_id: this.userId, session_date, session_type}, {emitEvent: false});
                    this.isEditing = false;
                }
                this.updateControlsState();
                // Clear the guard flag on the next tick.
                setTimeout(() => {
                    this.updatingForm = false;
                }, 0);
            });
    }

    /**
     * Calls the DialysisService to fetch old records based on the selected date and session type.
     */
    fetchOldData(selectedDate: Date, type: string) {
        const isoDate = selectedDate.toISOString();
        return this.dialysisService.getDialysisSessions(isoDate, isoDate, undefined, type).pipe(
            take(1),
            map(filteredSessions => {
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
     * Saves the current form data.
     * For providers, calls savePatientData; for patients, logs directly.
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
                        this.dialogMessage = 'Successfully saved.';
                        this.displayDialog = true;
                        this.resetForm();
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
                    next: response => {
                        console.log('Data saved successfully:', response);
                        this.dialogMessage = 'Successfully saved.';
                        this.displayDialog = true;
                        this.resetForm();
                    },
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
     * Opens a confirmation dialog before deleting the current session.
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
                    this.dialogMessage = 'Session deleted successfully.';
                    this.displayDialog = true;
                    this.resetForm();
                },
                error: err => {
                    console.error('Error deleting session:', err);
                    this.dialogMessage = 'Error deleting session. Please try again.';
                    this.displayDialog = true;
                }
            });
    }

    /**
     * Enables or disables form controls based on whether both session_date and session_type are set.
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

    resetForm(): void {
    const session_date = this.dialysisData.get('session_date')?.value;
    const session_type = this.dialysisData.get('session_type')?.value;

    this.dialysisData.reset({
        patient_id: this.userId,
        session_date
    });

    this.isEditing = false;
    this.updateControlsState();
    this.cdRef.detectChanges();
}

}