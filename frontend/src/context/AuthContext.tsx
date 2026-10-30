import React, { createContext, useState, useEffect, useContext } from "react";
import type { ReactNode } from "react";
import { loginUser, registerUser, refreshToken as refreshTokenAPI, getCurrentUser, logoutUser } from "../api/auth";

//import { logoutEvent } from "../api/api";

// --- Explicit User type
export interface User {
  id: number;
  username: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [accessToken, setAccessToken] = useState<string | null>(
    localStorage.getItem("token")
  );
  const [refreshTokenValue, setRefreshTokenValue] = useState<string | null>(
    localStorage.getItem("refresh")
  );

  // ✅ Helper to refresh tokens periodically or when 401 occurs
  const refresh = async () => {
  try {
    const newAccess = await refreshTokenAPI(); // no arguments

    if (newAccess) {
      setAccessToken(newAccess);
      localStorage.setItem("token", newAccess);

      const userData = await getCurrentUser();
      setUser(userData);

      console.log("🔄 Token refreshed successfully");
    } else {
      console.warn("⚠️ No access token returned, logging out");
      handleLogout();
    }
  } catch (error) {
    console.warn("❌ Token refresh failed", error);
    handleLogout();
  }
};

  // ✅ Login handler
  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      await loginUser(username, password);
      const userData = await getCurrentUser();
      setUser(userData);
    } finally {
      setLoading(false);
    }
  };

  // ✅ Register handler (auto-login after registration)
  const register = async (username: string, email: string, password: string) => {
    setLoading(true);
    try {
      await registerUser(username, email, password);
      const userData = await getCurrentUser();
      setUser(userData);
    } finally {
      setLoading(false);
    }
  };

  // ✅ Logout
  const handleLogout = () => {
    logoutUser();
    setUser(null);
  };

  // ✅ Initialize user on app mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
      } catch {
        // If token invalid or missing, do nothing
      } finally {
        setLoading(false);
      }
    };
    initAuth();
  }, []);

  const value: AuthContextType = {
    user,
    accessToken,
    refreshToken: refreshTokenValue, // map to context property
    loading,
    login,
    register,
    logout: handleLogout,
    refresh,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

