"use client"; // Required for Next.js App Router

import { useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "./services/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const { token, role } = await login(email, password);

      if (!token) {
        throw new Error("No token received. Login failed.");
      }

      console.log("🔹 Token received:", token);
      console.log("🔹 Role extracted:", role);

      //  Redirect based on role
      if (role === "provider") {
        router.push("/provider-dashboard");
      } else {
        router.push("/patient-dashboard");
      }
    } catch (err) {
      console.error(" Login failed:", err);
      setError("Invalid email or password. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <form onSubmit={handleLogin} className="bg-white p-6 rounded shadow-md w-96">
        <h2 className="text-2xl font-bold mb-4 text-center">Login</h2>
        {error && <p className="text-red-500 text-center">{error}</p>}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="border p-2 w-full mb-3 rounded"
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="border p-2 w-full mb-3 rounded"
        />

        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 w-full rounded"
          disabled={loading}
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
    </div>
  );
}
