"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { fetchProviderDashboard } from "../services/api"; //  Match import style
import { getUserRole } from "../../utils/auth"; //  Consistent with Patient Dashboard
import useDialysisLiveUpdates from "../services/useDialysisLiveUpdates"; //  Polling-based updates

export default function ProviderDashboard() {
  const [patients, setPatients] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const { data: liveData, error: liveError } = useDialysisLiveUpdates(); //  Use polling hook for live updates

  useEffect(() => {
    const token = localStorage.getItem("token");
    const role = getUserRole();

    if (!token || role !== "provider") {
      router.push("/login");
      return;
    }

    async function fetchData() {
      try {
        const data = await fetchProviderDashboard(token);

        //  Sort High-Risk Patients First
        const sortedPatients = Array.isArray(data)
          ? [...data].sort((a, b) => {
              const riskLevels = { High: 3, Medium: 2, Low: 1 };
              return riskLevels[b.risk_level] - riskLevels[a.risk_level];
            })
          : [];

        setPatients(sortedPatients);
      } catch (err) {
        console.error("Error fetching provider dashboard:", err);
        setError("Failed to load provider dashboard.");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  //  Sync real-time data updates
  useEffect(() => {
    if (Array.isArray(liveData)) {
      setPatients((prev) => {
        const patientMap = new Map(prev.map((p) => [p.patient_id, p])); //  Use `patient_id`
        liveData.forEach((p) => patientMap.set(p.patient_id, p));
        return Array.from(patientMap.values());
      });
    }
  }, [liveData]);

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Provider Dashboard</h1>

      {/*  Show Error Message */}
      {error && <p className="text-red-500">{error}</p>}
      {liveError && <p className="text-red-500">Live updates unavailable.</p>}

      {/*  Show Loading State */}
      {loading ? (
        <p className="text-gray-500">Loading patient data...</p>
      ) : patients.length > 0 ? (
        <ul className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Patient Overview</h2>
          {patients.map((patient, index) => (
            <li key={index} className={`border-b p-2 ${patient.risk_level === "High" ? "bg-red-100" : ""}`}>
              <strong>Name:</strong> {patient.patient_name || "Unknown"} -{" "}
              <strong>Effluent:</strong> {patient.avg_effluent ? `${patient.avg_effluent}L` : "N/A"} -{" "}
              <strong>Risk Level:</strong>{" "}
              <span className={patient.risk_level === "High" ? "text-red-500 font-bold" : "text-green-500"}>
                {patient.risk_level}
              </span>
              {patient.issues && (
                <ul className="text-sm text-gray-600">
                  {patient.issues.map((issue, i) => (
                    <li key={i}> {issue}</li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-500">No patients found.</p>
      )}
    </div>
  );
}
