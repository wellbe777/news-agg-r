// frontend/src/api/api.ts
import axios from "axios";
import { refreshToken } from "./auth";

export const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach access token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401: refresh token + retry original request
api.interceptors.response.use(
  (response) => response,

  async (error) => {
    const originalRequest = error.config;

    // Prevent infinite loop
    if (originalRequest._retry) {
      return Promise.reject(error);
    }

    // If access token expired
    if (error.response?.status === 401) {
      originalRequest._retry = true;

      const refresh = localStorage.getItem("refresh");
      if (!refresh) {
        console.warn("❌ No refresh token stored");
        localStorage.removeItem("access");
        window.location.href = "/login";
        return Promise.reject(error);
      }

      try {
        // refreshToken() must return: { access: string }
        const newTokens = await refreshToken();

        if (newTokens && newTokens.access) {
          localStorage.setItem("access", newTokens.access);

          // Apply new token to the failed request
          originalRequest.headers.Authorization = `Bearer ${newTokens.access}`;

          // Retry request
          return api(originalRequest);
        }
      } catch (err) {
        console.warn("❌ Refresh failed → logging out");

        localStorage.removeItem("access");
        localStorage.removeItem("refresh");

        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

export default api;
