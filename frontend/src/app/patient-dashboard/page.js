"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { fetchDialysisAnalytics } from "../services/api";
import DialysisChart from "../../components/DialysisChart";
import DialysisForm from "../../components/DialysisForm"; //  Import DialysisForm
import { getUserRole } from "../../utils/auth";
import useDialysisLiveUpdates from "../services/useDialysisLiveUpdates"; //  Polling-based updates

export default function PatientDashboard() {
  const [analytics, setAnalytics] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const { data: liveData, error: liveError } = useDialysisLiveUpdates(); //  Polling Hook

  useEffect(() => {
    const token = localStorage.getItem("token");
    const role = getUserRole();

    if (!token || role !== "patient") {
      router.push("/login");
      return;
    }

    async function fetchData() {
      try {
        const data = await fetchDialysisAnalytics(token);
        const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));
        setAnalytics(sortedData);
      } catch (err) {
        setError("Failed to load dialysis analytics.");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  //  Sync real-time data updates
  useEffect(() => {
    if (liveData) {
      setAnalytics((prev) => {
        const updatedAnalytics = [...prev, liveData].sort((a, b) => new Date(a.date) - new Date(b.date));
        return updatedAnalytics;
      });
    }
  }, [liveData]);

  //  Function to update analytics list when a new session is added
  const handleSessionAdded = (newSession) => {
    setAnalytics((prev) => [newSession, ...prev]); // Prepend new session to the list
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Patient Dashboard</h1>

      {/*  Show Error Messages */}
      {error && <p className="text-red-500">{error}</p>}
      {liveError && <p className="text-red-500">Live updates unavailable.</p>}

      {/*  Integrate DialysisForm */}
      <DialysisForm onSessionAdded={handleSessionAdded} /> {/*  Form Added Here */}

      {/*  Show Loading State */}
      {loading ? (
        <p className="text-gray-500">Loading analytics...</p>
      ) : analytics.length > 0 ? (
        <DialysisChart data={analytics} />
      ) : (
        <p className="text-gray-500">No analytics available yet.</p>
      )}
    </div>
  );
}
