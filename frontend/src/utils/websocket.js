import { useEffect, useState } from "react";
import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8004";

const useDialysisLiveUpdates = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token) {
      setError("No authentication token found.");
      return;
    }

    const fetchData = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/dialysis/live-updates`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setData(response.data);
      } catch (err) {
        console.error(" Error fetching live dialysis data:", err);
        setError("Failed to fetch data.");
      }
    };

    // Polling every 5 seconds
    const interval = setInterval(fetchData, 5000);
    fetchData(); // Initial fetch

    return () => clearInterval(interval); // Cleanup on unmount
  }, []);

  return { data, error };
};

export default useDialysisLiveUpdates;
