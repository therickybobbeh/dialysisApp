import { Component, Input, OnInit } from '@angular/core';
import { DialysisTreatmentData } from '../../Models/patientMeasurements';
import { DialysisSessionResponse } from '../../Models/dialysis';
import { DialysisService } from '../../Services/dialysis.service';
import { catchError, of, take } from 'rxjs';
import {Card} from "primeng/card";
import {PrimeTemplate} from "primeng/api";
import {ReactiveFormsModule} from "@angular/forms";
import {Calendar} from "primeng/calendar";
import {InputText} from "primeng/inputtext";
import {ButtonDirective, ButtonLabel} from "primeng/button";
import {DropdownModule} from "primeng/dropdown";
import {AuthService} from "../../Services/authentication.service";

@Component({
  selector: 'app-measurements',
  templateUrl: './measurements.component.html',
  styleUrls: ['./measurements.component.scss'],
  imports: [
    Card,
    PrimeTemplate,
    ReactiveFormsModule,
    Calendar,
    InputText,
    ButtonDirective,
    ButtonLabel,
    DropdownModule
  ],
  // ... imports array is in the template
})
export class MeasurementsComponent implements OnInit {
  @Input() selection: 'pre' | 'post' | undefined;
  allDialysisSessions: DialysisSessionResponse[] = [];
  measurementsTitle = 'Dialysis';

  // This is your reactive form group
  dialysisData: DialysisTreatmentData = new DialysisTreatmentData();

  // Options for the Session Type dropdown
  sessionTypes = [
    { label: 'Pre',  value: 'pre' },
    { label: 'Post', value: 'post' }
  ];

  private currentPatientId: string = '';


  constructor(private dialysisService: DialysisService,
              private  authService: AuthService) {}


  ngOnInit() {
    // We might want to populate some fields from localStorage here
    // e.g., this.dialysisData.patchValue({ patient_id: localStorage.getItem("user_id") });
    // But we've removed the patient_id from the template, so do it behind the scenes:
    this.currentPatientId = this.authService.getUserID();
    this.dialysisData.patchValue({ patient_id: this.currentPatientId });

    //fetch dialysis session for a date


    //todo: may not need
    this.dialysisService.getAllSessions()
        .pipe(take(1))
        .subscribe(sessions => {
          this.allDialysisSessions = sessions;
        });
  }

  saveData() {
    // The user’s patient_id can be set behind the scenes if needed.
    // e.g. let currentPatientId = localStorage.getItem('user_id');
    // this.dialysisData.patchValue({ patient_id: +currentPatientId });

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
            console.log('Logged dialysis data:', response);
          } else {
            console.log('Failed to log dialysis data.');
          }
        });
  }
}