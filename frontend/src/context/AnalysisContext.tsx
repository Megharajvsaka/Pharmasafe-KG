"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { CheckResponse } from "@/types/api";
import { api, ApiClientError } from "@/lib/api";

interface AnalysisContextType {
  selectedDrugs: string[];
  checkResult: CheckResponse | null;
  isLoading: boolean;
  error: string | null;
  addDrug: (name: string) => { success: boolean; reason?: string };
  removeDrug: (name: string) => void;
  clearDrugs: () => void;
  loadPreset: (drugs: string[]) => void;
  runAnalysis: (drugsOverride?: string[]) => Promise<CheckResponse | null>;
  resetAnalysis: () => void;
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined);

const STORAGE_KEY_DRUGS = "pharmasafe_selected_drugs";
const STORAGE_KEY_RESULTS = "pharmasafe_check_result";

export const AnalysisProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [selectedDrugs, setSelectedDrugs] = useState<string[]>([]);
  const [checkResult, setCheckResult] = useState<CheckResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isHydrated, setIsHydrated] = useState<boolean>(false);

  // Restore state from sessionStorage on mount
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
      // Ignore session storage parse error
    } finally {
      setIsHydrated(true);
    }
  }, []);

  // Sync to sessionStorage on change
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
      // Ignore session storage set error
    }
  }, [selectedDrugs, checkResult, isHydrated]);

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
    [selectedDrugs]
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

  return (
    <AnalysisContext.Provider
      value={{
        selectedDrugs,
        checkResult,
        isLoading,
        error,
        addDrug,
        removeDrug,
        clearDrugs,
        loadPreset,
        runAnalysis,
        resetAnalysis,
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
