/**
 * PharmaSafe-KG — Typed API Client
 * Connects to the FastAPI backend (default: http://localhost:8000)
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

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const headers = {
    "Content-Type": "application/json",
    ...(options?.headers || {}),
  };

  try {
    const res = await fetch(url, {
      ...options,
      headers,
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
};

export { ApiClientError };
export type { ApiError };
