/**
 * PharmaSafe-KG — TypeScript API Types
 * Corresponds exactly to FastAPI Pydantic models in phase3/app/models.py
 */

// ── Request Models ───────────────────────────────────────────────────────────

export interface CheckRequest {
  /** List of 2–10 Indian brand or generic drug names */
  drugs: string[];
}

// ── Response Models ──────────────────────────────────────────────────────────

export type MatchType = "exact" | "fuzzy" | "alias" | "generic_direct" | "not_found";

export interface ResolvedDrug {
  input: string;
  matched_brand: string;
  generics: string[];
  match_type: MatchType;
  confidence: number;
  review_required: boolean;
}

export type SeverityLevel = "MAJOR" | "MODERATE" | "MINOR" | "UNKNOWN" | "UNASSESSED";
export type InteractionStatus = "documented" | "predicted";
export type EvidenceSource = "knowledge_graph" | "gnn_predicted";

export interface EvidenceItem {
  source_id?: string;
  source?: string;
  mechanism?: string;
  severity?: string;
  model?: string;
  probability?: number;
  threshold?: number;
  evidence_type?: string;
  [key: string]: unknown;
}

export interface InteractionResult {
  brand_a: string;
  brand_b: string;
  ingredient_a: string;
  ingredient_b: string;
  severity: SeverityLevel;
  mechanism: string;
  explanation: string;
  status: InteractionStatus;
  source: EvidenceSource;
  confidence: number | null;
  evidence: EvidenceItem[];
}

export interface SafePair {
  brand_a: string;
  brand_b: string;
  note: string;
  status: "not_documented";
}

export interface CheckResponse {
  total_drugs: number;
  brand_names: string[];
  pairs_checked: number;
  interactions_found: number;
  safe_pairs: number;
  summary: string;
  interactions: InteractionResult[];
  safe_pairs_detail: SafePair[];
  resolved_drugs: ResolvedDrug[];
}

export interface DrugInteractionItem {
  interacting_ingredient: string;
  severity: "MAJOR" | "MODERATE" | "MINOR";
  mechanism: string;
  [key: string]: unknown;
}

export interface DrugInfoResponse {
  brand_name: string;
  generics: string[];
  total_known_ddis: number;
  major_count: number;
  moderate_count: number;
  minor_count: number;
  interactions: DrugInteractionItem[];
}

export interface GraphNode {
  id: string;
  label: string;
  type: "Drug" | "Ingredient";
  color: string;
  size: number;
}

export interface GraphEdge {
  from: string;
  to: string;
  label: string;
  color: string;
  width: number;
  title?: string;
  severity?: string;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface SearchResponse {
  query: string;
  results: string[];
  count: number;
}

export interface HealthResponse {
  status: string;
  neo4j: string;
  gnn_loaded: boolean;
  brands_loaded: number;
  version: string;
}

export interface ApiError {
  detail: string;
  status: number;
}
