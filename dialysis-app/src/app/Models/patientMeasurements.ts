import { FormControl, FormGroup, Validators } from '@angular/forms';

// Purpose: Contains the classes for the patient measurements before bed
export class PreDialysisTreatmentData extends FormGroup {
  constructor() {
    super({
      preDialysisWeight: new FormControl<number | null>(null, Validators.required),
      effluentVolume: new FormControl<number | null>(null, Validators.required),
      sessionDuration: new FormControl<number | null>(null, Validators.required),
      dailyProteinIntake: new FormControl<number | null>(null, Validators.required),
      bloodPressureBefore: new FormControl<number | null>(null, Validators.required)
    });
  }
}

export class PostDialysisTreatmentData extends FormGroup {
  constructor() {
    super({
      preDialysisWeight: new FormControl<number | null>(null, Validators.required),
      postDialysisWeight: new FormControl<number | null>(null, Validators.required),
      effluentVolume: new FormControl<number | null>(null, Validators.required),
      sessionDuration: new FormControl<number | null>(null, Validators.required),
      bloodPressureAfter: new FormControl<number | null>(null, Validators.required)
    });
  }
}