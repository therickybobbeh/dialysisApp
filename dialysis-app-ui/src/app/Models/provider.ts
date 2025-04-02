export interface ProviderDashboardRow {
    patient_id: number;
    patient_name: string;
    session_count: number;
    avg_pre_weight: number;
    avg_post_weight: number;
    avg_pre_systolic: number;
    avg_post_systolic: number;
    avg_effluent: number;
    risk_level: string;
    issues: string[];
}
