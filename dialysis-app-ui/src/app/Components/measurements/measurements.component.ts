import {AfterViewInit, Component, Input, OnDestroy, OnInit} from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { DialysisService } from '../../Services/dialysis.service';
import { AuthService } from '../../Services/authentication.service';
import { DialysisSessionResponse } from '../../Models/dialysis';
import {catchError, of, Subscription, take} from 'rxjs';
import { Calendar } from "primeng/calendar";
import { DropdownModule } from "primeng/dropdown";
import { Card } from "primeng/card";
import { InputText } from "primeng/inputtext";
import { ButtonDirective, ButtonLabel } from "primeng/button";
import { DialysisTreatmentData } from '../../Models/patientMeasurements';
import {DatePicker} from "primeng/datepicker";
import {Select} from "primeng/select"; // Import the class

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
    { label: 'Pre', value: 'pre' },
    { label: 'Post', value: 'post' }
  ];
  private currentPatientId: string = '';
  private subscription = new Subscription;

  constructor(
      private fb: FormBuilder,
      private dialysisService: DialysisService,
      private authService: AuthService
  ) {
    this.dialysisData = new DialysisTreatmentData();
  }



  ngOnInit() {
    this.currentPatientId = this.authService.getUserID();
    this.dialysisData.patchValue({ patient_id: this.currentPatientId });
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

  saveData() {
    this.dialysisService.logDialysisSession(this.dialysisData.value)
        .pipe(
            take(1),
            catchError(error => {
              console.error('Error logging dialysis data:', error);
              return of(null);
            })
        )
        .subscribe(response => {
          if (response) {
            this.dialysisData.reset();
            this.dialysisData = new DialysisTreatmentData();
            console.log('Logged dialysis data:', response);
          } else {
            console.log('Failed to log dialysis data.');
          }
        });
  }
}