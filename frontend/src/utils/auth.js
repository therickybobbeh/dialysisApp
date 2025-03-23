import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8004";

/**
 * Logs in the user and stores authentication tokens.
 */
export const login = async (credentials) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/auth/token`, credentials);
    const { access_token, refresh_token, user_role, user_id } = response.data;

    // Store tokens and user info
    localStorage.setItem("token", access_token);
    localStorage.setItem("refresh_token", refresh_token);
    localStorage.setItem("user_role", user_role);
    localStorage.setItem("user_id", user_id);

    return response.data;
  } catch (error) {
    console.error(" Login failed:", error.response?.data || error.message);
    throw error;
  }
};

/**
 * Logs out the user and clears session storage.
 */
export const logout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user_role");
  localStorage.removeItem("user_id");
  window.location.href = "/login"; // Redirect to login
};

/**
 * Checks if the user is authenticated.
 */
export const isAuthenticated = () => {
  return !!localStorage.getItem("token");
};

/**
 * Gets the currently logged-in user role.
 */
export const getUserRole = () => {
  return localStorage.getItem("user_role") || "guest";
};

/**
 * Refresh Token Function
 */
export const refreshToken = async () => {
  try {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
      logout();
      return null;
    }

    const response = await axios.post(`${API_BASE_URL}/auth/refresh`, { refresh_token: refreshToken });

    // Store new tokens
    localStorage.setItem("token", response.data.access_token);
    localStorage.setItem("refresh_token", response.data.refresh_token);

    return response.data.access_token;
  } catch (error) {
    console.error(" Refresh token failed. Logging out...");
    logout();
    return null;
  }
};

/**
 * Adds auth headers for API requests.
 */
export const authHeaders = () => {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};
