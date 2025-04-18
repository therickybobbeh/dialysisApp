export type AlertType = 'critical' | 'monitor' | 'information' | null;

export interface PatientAlerts {
    lowBloodPressure: AlertType;
    highBloodPressure: AlertType;
    dialysisGrowthAdjustment: AlertType;
    fluidOverloadHigh: AlertType;
    fluidOverloadWatch: AlertType;
    effluentVolume: AlertType;
    protein: AlertType;
    messages: AlertType;
}

export interface PatientAlertsFrontend {
    lowBloodPressure: {
        message: string;
        type: AlertType;
    };
    highBloodPressure: {
        message: string;
        type: AlertType;
    };
    dialysisGrowthAdjustment: {
        message: string;
        type: AlertType;
    };
    fluidOverloadHigh: {
        message: string;
        type: AlertType;
    };
    fluidOverloadWatch: {
        message: string;
        type: AlertType;
    };
    effluentVolume: {
        message: string;
        type: AlertType;
    };
    protein: {
        message: string;
        type: AlertType;
    };
}

export interface PatientAlertsBackend {
  lowBloodPressure: boolean;
  highBloodPressure: boolean;
  dialysisGrowthAdjustment: boolean;
  fluidOverloadHigh: boolean;
  fluidOverloadWatch: boolean;
  effluentVolume: boolean;
  protein: boolean;
}


export function mapBackendDataToPatientAlerts(data: PatientAlertsBackend): PatientAlertsFrontend {
  return {
    lowBloodPressure: {
      message: 'Low blood pressure detected.',
      type: data.lowBloodPressure ? 'critical' : null,
    },
    highBloodPressure: {
      message: 'High blood pressure detected.',
      type: data.highBloodPressure ? 'critical' : null,
    },
    dialysisGrowthAdjustment: {
      message: 'Dialysis growth adjustment needed.',
      type: data.dialysisGrowthAdjustment ? 'monitor' : null,
    },
    fluidOverloadHigh: {
      message: 'Fluid overload is critically high.',
      type: data.fluidOverloadHigh ? 'critical' : null,
    },
    fluidOverloadWatch: {
      message: 'Fluid overload is being monitored.',
      type: data.fluidOverloadWatch ? 'monitor' : null,
    },
    effluentVolume: {
      message: 'Effluent volume information.',
      type: data.effluentVolume ? 'information' : null,
    },
    protein: {
      message: 'Low protein intake detected.',
      type: data.protein ? 'information' : null,
    },
  };
}