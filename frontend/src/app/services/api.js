import axios from "axios";

// Base API URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8004";

// Create Axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

/**
 *  Refresh Token Function
 */
async function refreshToken() {
  try {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
      console.warn(" No refresh token found, redirecting to login.");
      logout();
      return null;
    }

    const response = await axios.post(`${API_BASE_URL}/auth/refresh`, { refresh_token: refreshToken });

    //  Store new tokens
    localStorage.setItem("token", response.data.access_token);
    localStorage.setItem("refresh_token", response.data.refresh_token);

    console.log(" Access token refreshed!");
    return response.data.access_token;
  } catch (error) {
    console.error(" Refresh token expired or invalid. Logging out...");
    logout();
    return null;
  }
}

/**
 *  Attach Authorization Token to Requests & Handle Expired Tokens
 */
apiClient.interceptors.request.use(async (config) => {
  let token = localStorage.getItem("token");

  if (token) {
    const isExpired = isTokenExpired(token);
    if (isExpired) {
      console.warn(" Access token expired, refreshing...");
      token = await refreshToken();
      if (!token) {
        return Promise.reject(new Error("Unauthorized"));
      }
    }
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

/**
 *  Axios Response Interceptor to Handle Token Expiration Globally
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      console.warn(" 401 Unauthorized - Trying to refresh token...");
      const newToken = await refreshToken();

      if (newToken) {
        error.config.headers.Authorization = `Bearer ${newToken}`;
        return apiClient.request(error.config);
      } else {
        console.warn(" Failed to refresh token. Logging out...");
        logout();
      }
    }
    return Promise.reject(error);
  }
);

/**
 *  Authentication API
 */
async function login(email, password) {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/auth/token`,
      new URLSearchParams({ username: email, password: password }),
      { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
    );

    const { access_token } = response.data;
    if (!access_token) throw new Error("No token received");

    //  Decode JWT Token to get user details
    const decoded = JSON.parse(atob(access_token.split(".")[1]));
    
    const user_id = decoded.user_id || decoded.sub; //  Ensure correct extraction
    const user_role = decoded.role;

    if (!user_id) {
      console.error("🚨 No user_id in JWT payload!");
      throw new Error("Invalid token: Missing user_id");
    }

    //  Store token, user_id, and role in localStorage
    localStorage.setItem("token", access_token);
    localStorage.setItem("user_id", String(user_id)); //  Store as string
    localStorage.setItem("user_role", user_role);

    console.log(" Login successful:", { user_id, user_role });

    return { token: access_token, user_id, role: user_role };
  } catch (error) {
    console.error(" Login failed:", error.response?.data || error.message);
    throw error;
  }
}


//  Logout function
function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user_role");
  localStorage.removeItem("user_id");
  window.location.href = "/login"; // Redirect to login
}

//  Helper function to check token expiration
function isTokenExpired(token) {
  try {
    const decoded = JSON.parse(atob(token.split(".")[1]));
    return decoded.exp * 1000 < Date.now();
  } catch (error) {
    return true; // Treat invalid tokens as expired
  }
}

/**
 *  API Calls for Patient & Provider Dashboards
 */

//  Fetch Dialysis Analytics (for Patient Dashboard)
async function fetchDialysisAnalytics() {
  try {
    const token = localStorage.getItem("token");
    if (!token) throw new Error("Unauthorized: No token found");

    const response = await axios.get(`${API_BASE_URL}/dialysis/analytics`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    return response.data;
  } catch (error) {
    console.error(" Error fetching analytics:", error.response?.data || error.message);
    throw error;
  }
}

//  Fetch Provider Dashboard Data
async function fetchProviderDashboard(page = 1, pageSize = 5) {
  try {
    const token = localStorage.getItem("token");
    if (!token) throw new Error("Unauthorized: No token found");

    const response = await axios.get(`${API_BASE_URL}/dialysis/provider-dashboard`, {
      params: { page, size: pageSize },
      headers: { Authorization: `Bearer ${token}` },
    });

    return response.data;
  } catch (error) {
    console.error(" Error fetching provider dashboard:", error.response?.data || error.message);
    throw error;
  }
}

// Register a new user
async function registerUser(userData) {
  try {
    return await apiClient.post("/auth/register", userData);
  } catch (error) {
    console.error(" Registration failed:", error.response?.data || error.message);
    throw error;
  }
}

//  Check if user is authenticated
function isAuthenticated() {
  return !!localStorage.getItem("token");
}

//  Get the current user role
function getUserRole() {
  return localStorage.getItem("user_role") || "guest";
}

//  Export functions
export {
  login,
  logout,
  apiClient,
  isTokenExpired,
  registerUser,
  isAuthenticated,
  getUserRole,
  fetchDialysisAnalytics,
  fetchProviderDashboard,
};
