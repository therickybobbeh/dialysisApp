export interface DialysisSessionCreate {
    session_type: string;
    session_id: number;
    patient_id: number;
    weight: number;
    diastolic: number;
    systolic: number;
    effluent_volume: number;
    session_date: string;  // or Date
    session_duration?: string;  // Optional field
}

//TODO: fix
export interface DialysisSessionResponse {
    id: number;
    patient_id: number;
    pre_weight: number;
    post_weight: number;
    pre_systolic: number;
    pre_diastolic: number;
    post_systolic: number;
    post_diastolic: number;
    effluent_volume: number;
    session_date: string;  // or ISO string
    // add other fields if your model has them (like user relationship)
}