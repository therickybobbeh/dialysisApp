import React, { useState } from "react";
import axios from "axios";
import { getUserRole, authHeaders } from "../utils/auth";
import { login } from "../app/services/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8004";

const DialysisForm = ({ onSessionAdded }) => {
  const [formData, setFormData] = useState({
    pre_weight: "",
    post_weight: "",
    pre_systolic: "",
    pre_diastolic: "",
    post_systolic: "",
    post_diastolic: "",
    effluent_volume: "",
    session_date: new Date().toISOString().slice(0, 16),
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
  
    try {
      const userRole = getUserRole();
      if (userRole !== "patient") {
        setError("Only patients can log dialysis sessions.");
        setLoading(false);
        return;
      }
  
      const patientId = localStorage.getItem("user_id");
      if (!patientId) {
        console.error(" Missing `user_id` in localStorage!");
        setError("User ID is missing. Please log in again.");
        setLoading(false);
        return;
      }
  
      const requestData = {
        patient_id: parseInt(patientId, 10),
        pre_weight: parseFloat(formData.pre_weight),
        post_weight: parseFloat(formData.post_weight),
        pre_systolic: parseInt(formData.pre_systolic, 10),
        pre_diastolic: parseInt(formData.pre_diastolic, 10),
        post_systolic: parseInt(formData.post_systolic, 10),
        post_diastolic: parseInt(formData.post_diastolic, 10),
        effluent_volume: parseFloat(formData.effluent_volume),
        session_date: formData.session_date,
      };
  
      console.log(" Sending request data:", requestData); //  Debugging log
  
      const response = await axios.post(
        `${API_BASE_URL}/dialysis/sessions`,
        requestData,
        { headers: authHeaders() }
      );
  
      console.log(" Response received:", response.data);
  
      onSessionAdded(response.data);
      setFormData({
        pre_weight: "",
        post_weight: "",
        pre_systolic: "",
        pre_diastolic: "",
        post_systolic: "",
        post_diastolic: "",
        effluent_volume: "",
        session_date: new Date().toISOString().slice(0, 16),
      });
  
      alert("Dialysis session logged successfully!");
    } catch (err) {
      console.error(" Error logging session:", err.response?.data || err.message);
  
      //  Handle Duplicate Session Error
      if (err.response?.data?.detail === "Dialysis session already logged today") {
        setError("⚠️ You have already logged a dialysis session today.");
        alert("⚠️ Duplicate Entry: You have already logged a dialysis session today.");
      } else {
        setError(err.response?.data?.detail || "Failed to log session.");
      }
    } finally {
      setLoading(false);
    }
  };
  
  
  
  

  return (
    <div className="max-w-lg mx-auto bg-white shadow-lg rounded-xl p-6 mt-6 border border-gray-200">
      <h2 className="text-2xl font-bold text-center text-blue-600 mb-4">Log Dialysis Session</h2>
      
      {error && <p className="text-red-500 text-center">{error}</p>}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Input Fields */}
        {[
          { label: "Pre-Dialysis Weight (kg)", name: "pre_weight" },
          { label: "Post-Dialysis Weight (kg)", name: "post_weight" },
          { label: "Pre-Dialysis Blood Pressure (Systolic)", name: "pre_systolic" },
          { label: "Pre-Dialysis Blood Pressure (Diastolic)", name: "pre_diastolic" },
          { label: "Post-Dialysis Blood Pressure (Systolic)", name: "post_systolic" },
          { label: "Post-Dialysis Blood Pressure (Diastolic)", name: "post_diastolic" },
          { label: "Effluent Volume (liters)", name: "effluent_volume" }
        ].map((field) => (
          <div key={field.name}>
            <label className="block text-gray-700 font-semibold">{field.label}:</label>
            <input
              type="number"
              name={field.name}
              value={formData[field.name]}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg p-2 text-gray-700 focus:ring focus:ring-blue-300 outline-none transition"
              required
            />
          </div>
        ))}

        {/* Session Date Field */}
        <div>
          <label className="block text-gray-700 font-semibold">Session Date:</label>
          <input
            type="datetime-local"
            name="session_date"
            value={formData.session_date}
            onChange={handleChange}
            className="w-full border border-gray-300 rounded-lg p-2 text-gray-700 focus:ring focus:ring-blue-300 outline-none transition"
            required
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-lg transition duration-300"
        >
          {loading ? "Logging..." : "Submit"}
        </button>
      </form>
    </div>
  );
};

export default DialysisForm;
