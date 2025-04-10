import { FormControl, FormGroup, Validators } from '@angular/forms';

// Purpose: Contains the classes for the patient measurements before bed
export class DialysisTreatmentData extends FormGroup {
  constructor() {
    super({
      session_type: new FormControl<string | null>(null, Validators.required),
      protein: new FormControl<number | null>(null, Validators.required),
      patient_id: new FormControl<number | null>(null, Validators.required),
      weight: new FormControl<number | null>(null, Validators.required),
      diastolic: new FormControl<number | null>(null, Validators.required),
      systolic: new FormControl<number | null>(null, Validators.required),
      effluent_volume: new FormControl<number | null>(null, Validators.required),
      session_date: new FormControl<string | null>(null, Validators.required),
      session_duration: new FormControl<string | null>(null)
    });
  }
}
