"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function Navbar() {
  const router = useRouter();
  const [role, setRole] = useState(null);

  useEffect(() => {
    const userRole = localStorage.getItem("role");
    setRole(userRole);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    router.push("/login");
  };

  return (
    <nav className="bg-blue-600 text-white p-4 flex justify-between">
      <div className="text-lg font-bold">PD Management</div>
      <div>
        {role === "provider" && (
          <a href="/dashboard" className="mr-4 hover:underline">Provider Dashboard</a>
        )}
        {role === "patient" && (
          <a href="/patient-dashboard" className="mr-4 hover:underline">Patient Dashboard</a>
        )}
        <button onClick={handleLogout} className="bg-red-500 px-3 py-1 rounded">Logout</button>
      </div>
    </nav>
  );
}
