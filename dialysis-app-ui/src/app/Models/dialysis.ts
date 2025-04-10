export interface DialysisSessionCreate {
    session_type: string;
    session_id: number;
    patient_id: number;
    weight: number;
    diastolic: number;
    systolic: number;
    effluent_volume: number;
    session_date: string;
    session_duration?: string;
    protein: number;
}

//TODO: fix
export interface DialysisSessionResponse {
    session_type: string;
    session_id: number;
    patient_id: number;
    weight: number;
    diastolic: number;
    systolic: number;
    effluent_volume: number;
    session_date: string;
    session_duration?: string;
    protein: number;
}