import { Component, Input, OnInit } from '@angular/core';
import { PreDialysisTreatmentData, PostDialysisTreatmentData} from "../../Models/patientMeasurements";
import {ReactiveFormsModule} from "@angular/forms";
import {InputText} from "primeng/inputtext";
import {NgIf} from "@angular/common";

@Component({
  selector: 'app-measurements',
  templateUrl: './measurements.component.html',
  imports: [
    ReactiveFormsModule,
    InputText,
    NgIf
  ],
  styleUrls: ['./measurements.component.scss']
})
export class MeasurementsComponent implements OnInit {
  //remove
  @Input() selection: 'pre' | 'post' | undefined;
  preDialysisData: PreDialysisTreatmentData = new PreDialysisTreatmentData();
  postDialysisData: PostDialysisTreatmentData = new PostDialysisTreatmentData();
  measurementsTitle: string = '';

  ngOnInit() {
    this.measurementsTitle = 'Dialysis'
  }
}