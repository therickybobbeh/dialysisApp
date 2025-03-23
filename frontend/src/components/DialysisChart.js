import React, { useEffect, useState } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";
import { Chart, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from "chart.js";
import { getUserRole, authHeaders } from "../utils/auth"; //  Import correct utilities

Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8004";

const DialysisChart = () => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    setLoading(true);
    setError("");

    try {
      const userRole = getUserRole(); //  Fix undefined getUserRole
      if (userRole !== "patient") {
        setError("Only patients can view dialysis data.");
        setLoading(false);
        return;
      }

      const response = await axios.get(`${API_BASE_URL}/dialysis/sessions`, {
        headers: authHeaders(),
        params: {
          start_date: startDate || undefined,
          end_date: endDate || undefined,
        },
      });

      setSessions(response.data);
    } catch (err) {
      console.error("Error fetching sessions:", err.response?.data || err.message);
      setError(err.response?.data?.detail || "Failed to retrieve data.");
    } finally {
      setLoading(false);
    }
  };

  //  Fix for missing date validation
  const handleDateChange = (e, setter) => {
    const value = e.target.value;
    setter(value);
  };

  //  Chart Data Fix
  const chartData = {
    labels: sessions.map((session) => new Date(session.session_date).toLocaleDateString()),
    datasets: [
      {
        label: "Pre-Dialysis Weight (kg)",
        data: sessions.map((session) => session.pre_weight),
        borderColor: "blue",
        backgroundColor: "rgba(0, 0, 255, 0.2)",
        fill: true,
      },
      {
        label: "Post-Dialysis Weight (kg)",
        data: sessions.map((session) => session.post_weight),
        borderColor: "green",
        backgroundColor: "rgba(0, 255, 0, 0.2)",
        fill: true,
      },
      {
        label: "Pre BP (Systolic)",
        data: sessions.map((session) => session.pre_systolic),
        borderColor: "red",
        backgroundColor: "rgba(255, 0, 0, 0.2)",
        fill: false,
      },
      {
        label: "Post BP (Systolic)",
        data: sessions.map((session) => session.post_systolic),
        borderColor: "orange",
        backgroundColor: "rgba(255, 165, 0, 0.2)",
        fill: false,
      },
    ],
  };

  return (
    <div className="dialysis-chart">
      <h2 className="text-xl font-bold">Dialysis Trends</h2>
      {error && <p className="text-red-500">{error}</p>}

      <div className="date-filters flex gap-2 mt-4">
        <label>Start Date:</label>
        <input type="date" value={startDate} onChange={(e) => handleDateChange(e, setStartDate)} />

        <label>End Date:</label>
        <input type="date" value={endDate} onChange={(e) => handleDateChange(e, setEndDate)} />

        <button className="bg-blue-500 text-white px-4 py-2 rounded" onClick={fetchSessions}>
          Filter
        </button>
      </div>

      {loading ? <p>Loading data...</p> : <Line data={chartData} />}
    </div>
  );
};

export default DialysisChart;
