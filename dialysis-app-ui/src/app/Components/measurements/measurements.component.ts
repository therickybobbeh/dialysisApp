import {AfterViewInit, Component, Input, OnDestroy, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, ReactiveFormsModule} from '@angular/forms';
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
import {PatientTableCard} from "../../Models/tables"; // Import the class

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
        Select
    ],
    styleUrls: ['./measurements.component.scss']
})
export class MeasurementsComponent implements OnInit, OnDestroy {
    @Input() selection: 'pre' | 'post' | undefined;
    allDialysisSessions: DialysisSessionResponse[] = [];
    measurementsTitle = 'Dialysis';
    dialysisData: DialysisTreatmentData; // Use the class
    sessionTypes = [
        {label: 'Pre', value: 'pre'},
        {label: 'Post', value: 'post'}
    ];
    private currentPatientId: number = -1;
    private subscription = new Subscription;
    private selectedPatient: PatientTableCard | null = null;

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
        this.subscription.add(
            this.dialysisData.get('session_date')?.valueChanges.subscribe(dateRange => {
                if (dateRange && dateRange.length === 2) {
                    const [startDate, endDate] = dateRange;
                    this.fetchSessions(startDate, endDate);
                }
            })
        );
        // this.dialysisService.getAllSessions()
        //     .pipe(take(1))
        //     .subscribe(sessions => {
        //       this.allDialysisSessions = sessions;
        //     });
    }

    ngOnDestroy() {
        this.subscription.unsubscribe()
    }

    fetchSessions(startDate: Date, endDate: Date) {
        //todo: change to one ay

        // this.dialysisService.getSessionsByDateRange(startDate, endDate)
        //     .pipe(
        //         take(1),
        //         catchError(error => {
        //           console.error('Error fetching dialysis sessions:', error);
        //           return of([]);
        //         })
        //     )
        //     .subscribe(sessions => {
        //       this.allDialysisSessions = sessions;
        //     });
    }

    // saveData() {
    //     this.dialysisService.logDialysisSession(this.dialysisData.value)
    //         .pipe(
    //             take(1),
    //             catchError(error => {
    //                 console.error('Error logging dialysis data:', error);
    //                 return of(null);
    //             })
    //         )
    //         .subscribe(response => {
    //             if (response) {
    //                 this.dialysisData.reset();
    //                 this.dialysisData = new DialysisTreatmentData();
    //                 console.log('Logged dialysis data:', response);
    //             } else {
    //                 console.log('Failed to log dialysis data.');
    //             }
    //         });
    // }
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
}