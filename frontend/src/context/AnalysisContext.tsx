"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { CheckResponse } from "@/types/api";
import { api, ApiClientError } from "@/lib/api";
import { useAuth } from "./AuthContext";

export interface RecentAnalysisItem {
  id: string;
  drugs: string[];
  timestamp: string;
  totalFound: number;
  majorCount: number;
  moderateCount: number;
}

export interface SavedRegimenItem {
  id: string;
  name: string;
  drugs: string[];
  createdAt: string;
}

interface AnalysisContextType {
  selectedDrugs: string[];
  checkResult: CheckResponse | null;
  isLoading: boolean;
  error: string | null;
  recentAnalyses: RecentAnalysisItem[];
  savedRegimens: SavedRegimenItem[];
  addDrug: (name: string) => { success: boolean; reason?: string };
  removeDrug: (name: string) => void;
  clearDrugs: () => void;
  loadPreset: (drugs: string[]) => void;
  runAnalysis: (drugsOverride?: string[]) => Promise<CheckResponse | null>;
  resetAnalysis: () => void;
  saveRegimen: (name: string, drugs?: string[]) => Promise<boolean>;
  deleteSavedRegimen: (id: string) => Promise<void>;
  clearRecentAnalyses: () => void;
  refreshWorkspaceData: () => Promise<void>;
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined);

const STORAGE_KEY_DRUGS = "pharmasafe_selected_drugs";
const STORAGE_KEY_RESULTS = "pharmasafe_check_result";

const DEFAULT_CLINICAL_TEMPLATES: SavedRegimenItem[] = [
  {
    id: "reg_cardiac_default",
    name: "Cardiology Standard Regimen",
    drugs: ["Atorva 10", "Ecosprin", "Metolar XR"],
    createdAt: new Date().toLocaleDateString(),
  },
  {
    id: "reg_warfarin_default",
    name: "Anticoagulation GI Monitoring",
    drugs: ["Warfarin", "Combiflam", "Pantop 40"],
    createdAt: new Date().toLocaleDateString(),
  },
];

export const AnalysisProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isAuthenticated } = useAuth();

  const [selectedDrugs, setSelectedDrugs] = useState<string[]>([]);
  const [checkResult, setCheckResult] = useState<CheckResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [recentAnalyses, setRecentAnalyses] = useState<RecentAnalysisItem[]>([]);
  const [savedRegimens, setSavedRegimens] = useState<SavedRegimenItem[]>(DEFAULT_CLINICAL_TEMPLATES);
  const [isHydrated, setIsHydrated] = useState<boolean>(false);

  // Restore session drug selections
  useEffect(() => {
    try {
      const storedDrugs = sessionStorage.getItem(STORAGE_KEY_DRUGS);
      if (storedDrugs) {
        setSelectedDrugs(JSON.parse(storedDrugs));
      }
      const storedResult = sessionStorage.getItem(STORAGE_KEY_RESULTS);
      if (storedResult) {
        setCheckResult(JSON.parse(storedResult));
      }
    } catch {
      // ignore
    } finally {
      setIsHydrated(true);
    }
  }, []);

  // Sync session state
  useEffect(() => {
    if (!isHydrated) return;
    try {
      sessionStorage.setItem(STORAGE_KEY_DRUGS, JSON.stringify(selectedDrugs));
      if (checkResult) {
        sessionStorage.setItem(STORAGE_KEY_RESULTS, JSON.stringify(checkResult));
      } else {
        sessionStorage.removeItem(STORAGE_KEY_RESULTS);
      }
    } catch {
      // ignore
    }
  }, [selectedDrugs, checkResult, isHydrated]);

  // Load server-backed Regimens & History when authenticated
  const refreshWorkspaceData = useCallback(async () => {
    if (!isAuthenticated) {
      setSavedRegimens(DEFAULT_CLINICAL_TEMPLATES);
      setRecentAnalyses([]);
      return;
    }

    try {
      // Fetch PostgreSQL saved regimens
      const serverRegimens = await api.getSavedRegimens();
      if (serverRegimens && Array.isArray(serverRegimens)) {
        setSavedRegimens(
          serverRegimens.map((r) => ({
            id: r.id,
            name: r.name,
            drugs: r.drugs,
            createdAt: new Date(r.created_at).toLocaleDateString(),
          }))
        );
      }

      // Fetch PostgreSQL analysis history
      const serverHistory = await api.getAnalysisHistory(20);
      if (serverHistory && Array.isArray(serverHistory)) {
        setRecentAnalyses(
          serverHistory.map((h) => {
            const summary = h.result_summary || {};
            return {
              id: h.id,
              drugs: h.drugs,
              timestamp: new Date(h.created_at).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              }),
              totalFound: summary.interactions_found || summary.total || 0,
              majorCount: summary.major_count || summary.major || 0,
              moderateCount: summary.moderate_count || summary.moderate || 0,
            };
          })
        );
      }
    } catch (err) {
      console.warn("Notice: Could not sync with PostgreSQL workspace data:", err);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    refreshWorkspaceData();
  }, [isAuthenticated, user?.id, refreshWorkspaceData]);

  const addDrug = useCallback(
    (name: string): { success: boolean; reason?: string } => {
      const cleanName = name.trim();
      if (!cleanName) {
        return { success: false, reason: "Drug name cannot be empty." };
      }
      if (selectedDrugs.length >= 10) {
        return { success: false, reason: "Maximum 10 medications can be checked at once." };
      }
      const isDuplicate = selectedDrugs.some(
        (d) => d.toLowerCase() === cleanName.toLowerCase()
      );
      if (isDuplicate) {
        return { success: false, reason: `"${cleanName}" is already in your medication list.` };
      }

      setSelectedDrugs((prev) => [...prev, cleanName]);
      setError(null);
      return { success: true };
    },
    [selectedDrugs]
  );

  const removeDrug = useCallback((name: string) => {
    setSelectedDrugs((prev) => prev.filter((d) => d.toLowerCase() !== name.toLowerCase()));
  }, []);

  const clearDrugs = useCallback(() => {
    setSelectedDrugs([]);
    setCheckResult(null);
    setError(null);
    try {
      sessionStorage.removeItem(STORAGE_KEY_DRUGS);
      sessionStorage.removeItem(STORAGE_KEY_RESULTS);
    } catch {
      // ignore
    }
  }, []);

  const loadPreset = useCallback((drugs: string[]) => {
    const validDrugs = drugs.map((d) => d.trim()).filter(Boolean).slice(0, 10);
    setSelectedDrugs(validDrugs);
    setCheckResult(null);
    setError(null);
  }, []);

  const runAnalysis = useCallback(
    async (drugsOverride?: string[]): Promise<CheckResponse | null> => {
      const drugsToAnalyze = drugsOverride || selectedDrugs;
      if (drugsToAnalyze.length < 2) {
        const msg = "Please add at least 2 medications to check interactions.";
        setError(msg);
        return null;
      }
      if (drugsToAnalyze.length > 10) {
        const msg = "Maximum 10 medications supported per analysis.";
        setError(msg);
        return null;
      }

      setIsLoading(true);
      setError(null);

      try {
        const result = await api.checkInteractions(drugsToAnalyze);
        setCheckResult(result);

        const majorHits = result.interactions.filter((i) => i.severity === "MAJOR").length;
        const modHits = result.interactions.filter((i) => i.severity === "MODERATE").length;

        const summaryData = {
          interactions_found: result.interactions_found,
          major_count: majorHits,
          moderate_count: modHits,
          safe_pairs: result.safe_pairs,
          total_drugs: result.total_drugs,
        };

        // Persist to PostgreSQL if authenticated
        if (isAuthenticated) {
          try {
            const savedItem = await api.saveAnalysisHistory(drugsToAnalyze, summaryData);
            const newRecentItem: RecentAnalysisItem = {
              id: savedItem.id,
              drugs: [...drugsToAnalyze],
              timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
              totalFound: result.interactions_found,
              majorCount: majorHits,
              moderateCount: modHits,
            };
            setRecentAnalyses((prev) => [newRecentItem, ...prev.slice(0, 19)]);
          } catch {
            // fallback to memory
            const localItem: RecentAnalysisItem = {
              id: "hist_" + Date.now(),
              drugs: [...drugsToAnalyze],
              timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
              totalFound: result.interactions_found,
              majorCount: majorHits,
              moderateCount: modHits,
            };
            setRecentAnalyses((prev) => [localItem, ...prev.slice(0, 9)]);
          }
        } else {
          const localItem: RecentAnalysisItem = {
            id: "hist_" + Date.now(),
            drugs: [...drugsToAnalyze],
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
            totalFound: result.interactions_found,
            majorCount: majorHits,
            moderateCount: modHits,
          };
          setRecentAnalyses((prev) => [localItem, ...prev.slice(0, 9)]);
        }

        return result;
      } catch (err) {
        const errorMsg =
          err instanceof ApiClientError ? err.detail : "An unexpected error occurred during analysis.";
        setError(errorMsg);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [selectedDrugs, isAuthenticated]
  );

  const resetAnalysis = useCallback(() => {
    setCheckResult(null);
    setError(null);
    try {
      sessionStorage.removeItem(STORAGE_KEY_RESULTS);
    } catch {
      // ignore
    }
  }, []);

  const saveRegimen = useCallback(
    async (name: string, drugs?: string[]): Promise<boolean> => {
      const drugsToSave = drugs || selectedDrugs;
      if (!name.trim() || drugsToSave.length < 2) return false;

      if (isAuthenticated) {
        try {
          const saved = await api.createSavedRegimen(name.trim(), drugsToSave);
          const newReg: SavedRegimenItem = {
            id: saved.id,
            name: saved.name,
            drugs: saved.drugs,
            createdAt: new Date(saved.created_at).toLocaleDateString(),
          };
          setSavedRegimens((prev) => [newReg, ...prev]);
          return true;
        } catch (err) {
          console.error("Error saving regimen to PostgreSQL:", err);
          return false;
        }
      } else {
        const newReg: SavedRegimenItem = {
          id: "reg_" + Date.now(),
          name: name.trim(),
          drugs: [...drugsToSave],
          createdAt: new Date().toLocaleDateString(),
        };
        setSavedRegimens((prev) => [newReg, ...prev]);
        return true;
      }
    },
    [selectedDrugs, isAuthenticated]
  );

  const deleteSavedRegimen = useCallback(
    async (id: string) => {
      if (isAuthenticated && !id.startsWith("reg_")) {
        try {
          await api.deleteSavedRegimen(id);
        } catch (err) {
          console.error("Error deleting regimen from PostgreSQL:", err);
        }
      }
      setSavedRegimens((prev) => prev.filter((r) => r.id !== id));
    },
    [isAuthenticated]
  );

  const clearRecentAnalyses = useCallback(() => {
    setRecentAnalyses([]);
  }, []);

  return (
    <AnalysisContext.Provider
      value={{
        selectedDrugs,
        checkResult,
        isLoading,
        error,
        recentAnalyses,
        savedRegimens,
        addDrug,
        removeDrug,
        clearDrugs,
        loadPreset,
        runAnalysis,
        resetAnalysis,
        saveRegimen,
        deleteSavedRegimen,
        clearRecentAnalyses,
        refreshWorkspaceData,
      }}
    >
      {children}
    </AnalysisContext.Provider>
  );
};

export const useAnalysis = () => {
  const context = useContext(AnalysisContext);
  if (!context) {
    throw new Error("useAnalysis must be used within an AnalysisProvider");
  }
  return context;
};
