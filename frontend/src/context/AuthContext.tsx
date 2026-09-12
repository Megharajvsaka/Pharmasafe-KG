"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { api, ApiClientError, setAccessToken, UserProfileResponse } from "@/lib/api";

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: "clinician" | "researcher" | "student" | "faculty" | "admin";
  institution?: string;
  avatarInitials: string;
  createdAt?: string;
}

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; role?: string; error?: string }>;
  register: (
    name: string,
    email: string,
    password: string,
    institution?: string,
    role?: string
  ) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  forgotPassword: (email: string) => Promise<{ success: boolean; message?: string; error?: string }>;
  resetPassword: (password: string) => Promise<{ success: boolean; error?: string }>;
  refreshSession: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function mapDtoToProfile(dto: UserProfileResponse): UserProfile {
  const name = dto.full_name || "PharmaSafe User";
  const initials = name
    .split(" ")
    .map((n) => n[0])
    .filter(Boolean)
    .join("")
    .substring(0, 2)
    .toUpperCase() || "PS";

  return {
    id: dto.id,
    name: dto.full_name,
    email: dto.email,
    role: (dto.role?.toLowerCase() as any) || "researcher",
    institution: dto.institution || undefined,
    avatarInitials: initials,
    createdAt: dto.created_at,
  };
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Restore authenticated session from PostgreSQL backend via refresh cookie on mount
  useEffect(() => {
    let mounted = true;

    async function restoreSession() {
      try {
        // Attempt silent session refresh via HttpOnly cookie
        const res = await api.refreshToken();
        if (mounted && res && res.user) {
          setUser(mapDtoToProfile(res.user));
        }
      } catch {
        // If refresh fails, try /auth/me in case access token is valid
        try {
          const me = await api.getMe();
          if (mounted && me) {
            setUser(mapDtoToProfile(me));
          }
        } catch {
          if (mounted) {
            setUser(null);
            setAccessToken(null);
          }
        }
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    }

    restoreSession();

    return () => {
      mounted = false;
    };
  }, []);

  const refreshSession = useCallback(async (): Promise<boolean> => {
    try {
      const res = await api.refreshToken();
      if (res && res.user) {
        setUser(mapDtoToProfile(res.user));
        return true;
      }
      return false;
    } catch {
      setUser(null);
      setAccessToken(null);
      return false;
    }
  }, []);

  const login = useCallback(
    async (email: string, password: string): Promise<{ success: boolean; role?: string; error?: string }> => {
      setIsLoading(true);
      try {
        const res = await api.login({ email, password });
        const profile = mapDtoToProfile(res.user);
        setUser(profile);
        return { success: true, role: profile.role };
      } catch (err) {
        const msg =
          err instanceof ApiClientError
            ? err.detail
            : "Unable to sign in. Please verify your connection to the server.";
        return { success: false, error: msg };
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const register = useCallback(
    async (
      name: string,
      email: string,
      password: string,
      institution?: string,
      role: string = "researcher"
    ): Promise<{ success: boolean; error?: string }> => {
      setIsLoading(true);
      try {
        const res = await api.register({
          full_name: name,
          email,
          password,
          institution: institution || undefined,
          role,
        });
        setUser(mapDtoToProfile(res.user));
        return { success: true };
      } catch (err) {
        const msg =
          err instanceof ApiClientError
            ? err.detail
            : "Registration failed. Please check your details and try again.";
        return { success: false, error: msg };
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await api.logout();
    } catch {
      // ignore network errors on logout
    } finally {
      setUser(null);
      setAccessToken(null);
      setIsLoading(false);
    }
  }, []);

  const forgotPassword = useCallback(
    async (email: string): Promise<{ success: boolean; message?: string; error?: string }> => {
      const clean = email.trim().toLowerCase();
      if (!clean || !clean.includes("@")) {
        return { success: false, error: "Please enter a valid institutional email address." };
      }
      // Accurate scientific disclosure: email server pending configuration
      return {
        success: false,
        error:
          "SMTP email service is not yet configured on this research server. Please contact your system administrator for password recovery.",
      };
    },
    []
  );

  const resetPassword = useCallback(
    async (password: string): Promise<{ success: boolean; error?: string }> => {
      if (!password || password.length < 8) {
        return { success: false, error: "Password must be at least 8 characters long." };
      }
      return {
        success: false,
        error:
          "Direct password reset requires a valid one-time security token issued via institutional email.",
      };
    },
    []
  );

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        forgotPassword,
        resetPassword,
        refreshSession,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
