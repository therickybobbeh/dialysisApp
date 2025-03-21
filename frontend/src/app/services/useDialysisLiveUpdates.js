import { useEffect, useState } from "react";
import axios from "axios";
import { getUserRole } from "../../utils/auth";
import { apiClient } from "../services/api"; //  Use centralized API client

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8004";

const useDialysisLiveUpdates = () => {
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const role = getUserRole();

    if (!token) {
      setError("No authentication token found.");
      return;
    }

    const endpoint =
      role === "provider"
        ? `${API_BASE_URL}/dialysis/provider/live-updates`
        : `${API_BASE_URL}/dialysis/patient/live-updates`;

    console.log(` Fetching Live Updates from: ${endpoint}`);

    const fetchData = async () => {
      try {
        const response = await apiClient.get(endpoint); //  Uses refreshed token
        if (response.status === 200) {
          setData(Array.isArray(response.data) ? response.data : []);
        }
      } catch (err) {
        if (err.response?.status === 401) {
          console.error(" Unauthorized: Token expired.");
          setError("Session expired. Please log in again.");
          localStorage.removeItem("token");
          window.location.href = "/login"; // Redirect on failure
        } else if (err.response?.status === 404) {
          console.warn(" No new updates available.");
          setData([]);
        } else {
          console.error(" Error fetching live dialysis data:", err);
          setError("Failed to fetch live updates.");
        }
      }
    };

    fetchData(); // Initial fetch
    const interval = setInterval(fetchData, 50000); //  Polling every 50s

    return () => clearInterval(interval);
  }, []);

  return { data, error };
};

export default useDialysisLiveUpdates;
