/**
 * PharmaSafe-KG — Typed API Client
 * Connects to the FastAPI backend with PostgreSQL authentication and Neo4j DDI engine.
 */

import {
  HealthResponse,
  SearchResponse,
  CheckResponse,
  DrugInfoResponse,
  GraphResponse,
  ApiError,
} from "@/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

let _accessToken: string | null = null;

export interface UserProfileResponse {
  id: string;
  email: string;
  full_name: string;
  role: string;
  institution?: string | null;
  is_active: boolean;
  created_at: string;
}

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserProfileResponse;
}

export interface SavedRegimenDTO {
  id: string;
  user_id: string;
  name: string;
  drugs: string[];
  created_at: string;
  updated_at: string;
}

export interface AnalysisHistoryDTO {
  id: string;
  user_id: string;
  drugs: string[];
  result_summary: Record<string, any>;
  created_at: string;
}

export interface AdminUserDTO {
  id: string;
  email: string;
  full_name: string;
  role: string;
  institution?: string | null;
  is_active: boolean;
  created_at: string;
}

export interface AdminStatsDTO {
  total_users: number;
  users_by_role: Record<string, number>;
  total_regimens: number;
  total_analyses: number;
  total_brands_mapped: number;
  total_graph_nodes: number;
  total_graph_relationships: number;
  gnn_active: boolean;
}

class ApiClientError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(`API Error ${status}: ${detail}`);
    this.name = "ApiClientError";
    this.status = status;
    this.detail = detail;
  }
}

export function setAccessToken(token: string | null) {
  _accessToken = token;
}

export function getAccessToken(): string | null {
  return _accessToken;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options?.headers as Record<string, string>) || {}),
  };

  if (_accessToken && !headers["Authorization"]) {
    headers["Authorization"] = `Bearer ${_accessToken}`;
  }

  try {
    const res = await fetch(url, {
      ...options,
      headers,
      credentials: "include", // Essential for HttpOnly refresh cookie exchange
    });

    if (!res.ok) {
      let detail = `Request failed with status ${res.status}`;
      try {
        const errorData = await res.json();
        if (errorData && typeof errorData.detail === "string") {
          detail = errorData.detail;
        } else if (errorData && typeof errorData.detail === "object") {
          detail = JSON.stringify(errorData.detail);
        }
      } catch {
        // use default status message if body is not JSON
      }
      throw new ApiClientError(res.status, detail);
    }

    return (await res.json()) as T;
  } catch (error) {
    if (error instanceof ApiClientError) {
      throw error;
    }
    const message = error instanceof Error ? error.message : "Network error";
    throw new ApiClientError(0, `Cannot connect to PharmaSafe-KG backend (${API_BASE}). ${message}`);
  }
}

export const api = {
  // ── Public Research & Knowledge Graph APIs ────────────────────────────────

  /**
   * Health check endpoint — tests API status, Neo4j connection, and GNN availability
   */
  async getHealth(): Promise<HealthResponse> {
    return request<HealthResponse>("/health");
  },

  /**
   * Autocomplete search for Indian brand drug names
   */
  async searchBrands(query: string, limit = 10): Promise<SearchResponse> {
    const cleanQuery = query.trim();
    if (!cleanQuery) {
      return { query: "", results: [], count: 0 };
    }
    const params = new URLSearchParams({
      q: cleanQuery,
      limit: String(limit),
    });
    return request<SearchResponse>(`/search?${params.toString()}`);
  },

  /**
   * Core Polypharmacy Interaction Check (2–10 drugs)
   */
  async checkInteractions(drugs: string[]): Promise<CheckResponse> {
    const cleaned = drugs.map((d) => d.trim()).filter(Boolean);
    if (cleaned.length < 2) {
      throw new ApiClientError(422, "At least 2 drug names are required to check interactions.");
    }
    if (cleaned.length > 10) {
      throw new ApiClientError(422, "Maximum 10 drugs can be checked at once.");
    }

    return request<CheckResponse>("/check", {
      method: "POST",
      body: JSON.stringify({ drugs: cleaned }),
    });
  },

  /**
   * Full drug monograph detail lookup
   */
  async getDrugInfo(brandName: string): Promise<DrugInfoResponse> {
    const encoded = encodeURIComponent(brandName.trim());
    return request<DrugInfoResponse>(`/drug/${encoded}`);
  },

  /**
   * Interactive graph network data for visualization
   */
  async getGraph(drugs: string[]): Promise<GraphResponse> {
    const cleaned = drugs.map((d) => d.trim()).filter(Boolean);
    if (cleaned.length < 2) {
      throw new ApiClientError(422, "At least 2 drugs are required for graph visualization.");
    }
    const params = new URLSearchParams();
    cleaned.forEach((d) => params.append("drugs", d));
    return request<GraphResponse>(`/graph?${params.toString()}`);
  },

  // ── PostgreSQL Authentication APIs ─────────────────────────────────────────

  /**
   * Register a new user account with PostgreSQL
   */
  async register(payload: {
    email: string;
    password: string;
    full_name: string;
    role?: string;
    institution?: string;
  }): Promise<AuthTokenResponse> {
    const res = await request<AuthTokenResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setAccessToken(res.access_token);
    return res;
  },

  /**
   * Authenticate user against PostgreSQL and obtain JWT + HttpOnly refresh cookie
   */
  async login(payload: { email: string; password: string }): Promise<AuthTokenResponse> {
    const res = await request<AuthTokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setAccessToken(res.access_token);
    return res;
  },

  /**
   * Revoke refresh token and log out of session
   */
  async logout(): Promise<{ message: string; status: string }> {
    try {
      const res = await request<{ message: string; status: string }>("/auth/logout", {
        method: "POST",
      });
      return res;
    } finally {
      setAccessToken(null);
    }
  },

  /**
   * Fetch current user profile from PostgreSQL
   */
  async getMe(): Promise<UserProfileResponse> {
    return request<UserProfileResponse>("/auth/me");
  },

  /**
   * Refresh session and obtain new access JWT using HttpOnly cookie
   */
  async refreshToken(): Promise<AuthTokenResponse> {
    const res = await request<AuthTokenResponse>("/auth/refresh", {
      method: "POST",
    });
    setAccessToken(res.access_token);
    return res;
  },

  // ── Saved Regimens (PostgreSQL Persisted) ───────────────────────────────────

  async getSavedRegimens(): Promise<SavedRegimenDTO[]> {
    return request<SavedRegimenDTO[]>("/users/me/regimens");
  },

  async createSavedRegimen(name: string, drugs: string[]): Promise<SavedRegimenDTO> {
    return request<SavedRegimenDTO>("/users/me/regimens", {
      method: "POST",
      body: JSON.stringify({ name: name.trim(), drugs }),
    });
  },

  async deleteSavedRegimen(id: string): Promise<{ message: string; status: string }> {
    return request<{ message: string; status: string }>(`/users/me/regimens/${id}`, {
      method: "DELETE",
    });
  },

  // ── Analysis History (PostgreSQL Persisted) ────────────────────────────────

  async getAnalysisHistory(limit = 20): Promise<AnalysisHistoryDTO[]> {
    return request<AnalysisHistoryDTO[]>(`/users/me/history?limit=${limit}`);
  },

  async saveAnalysisHistory(
    drugs: string[],
    resultSummary: Record<string, any>
  ): Promise<AnalysisHistoryDTO> {
    return request<AnalysisHistoryDTO>("/users/me/history", {
      method: "POST",
      body: JSON.stringify({ drugs, result_summary: resultSummary }),
    });
  },

  // ── Administrative Console (Admin Token Required) ──────────────────────────

  async getAdminUsers(): Promise<AdminUserDTO[]> {
    return request<AdminUserDTO[]>("/admin/users");
  },

  async getAdminStats(): Promise<AdminStatsDTO> {
    return request<AdminStatsDTO>("/admin/stats");
  },
};

export { ApiClientError };
export type { ApiError };
