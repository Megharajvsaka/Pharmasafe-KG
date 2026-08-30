"use client";

import React from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  FlaskConical,
  Search,
  Trash2,
  ArrowRight,
  ShieldCheck,
  Sparkles,
  Info,
  Pill,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/feedback/EmptyState";
import { ErrorState } from "@/components/feedback/ErrorState";
import { useToast } from "@/components/feedback/Toast";
import { DrugSearchBar } from "@/components/drugs/DrugSearchBar";
import { DrugChip } from "@/components/drugs/DrugChip";
import { PresetSelector } from "@/components/drugs/PresetSelector";
import { useAnalysis } from "@/context/AnalysisContext";

export default function AnalyzePage() {
  const router = useRouter();
  const { showToast } = useToast();
  const {
    selectedDrugs,
    isLoading,
    error,
    addDrug,
    removeDrug,
    clearDrugs,
    loadPreset,
    runAnalysis,
  } = useAnalysis();

  const handleSelectDrug = (name: string) => {
    const result = addDrug(name);
    if (!result.success && result.reason) {
      showToast("error", "Cannot Add Medication", result.reason);
    }
  };

  const handleSelectPreset = (presetDrugs: string[]) => {
    loadPreset(presetDrugs);
    showToast("info", "Preset Regimen Loaded", `Loaded ${presetDrugs.length} medications.`);
  };

  const handleCheckInteractions = async () => {
    if (selectedDrugs.length < 2) {
      showToast("error", "Validation Error", "Please select at least 2 medications.");
      return;
    }

    const result = await runAnalysis();
    if (result) {
      router.push("/results");
    }
  };

  const isMaxReached = selectedDrugs.length >= 10;
  const isSubmitDisabled = selectedDrugs.length < 2 || selectedDrugs.length > 10 || isLoading;

  return (
    <div className="w-full pb-16">
      {/* Top Header Bar */}
      <div className="bg-white border-b border-slate-200 py-6">
        <PageContainer>
          <Breadcrumbs items={[{ label: "Medication Workbench" }]} className="mb-2" />
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-left">
            <div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-sky-600 flex items-center justify-center text-white">
                  <FlaskConical className="w-4 h-4" />
                </div>
                <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                  Medication Interaction Workbench
                </h1>
              </div>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Enter 2–10 commercial Indian brand or generic drug names to evaluate polypharmacy interactions.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Link href="/demo">
                <Button variant="outline" size="sm">
                  View Demo Scenarios
                </Button>
              </Link>
            </div>
          </div>
        </PageContainer>
      </div>

      <PageContainer className="pt-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 text-left">
          {/* ── LEFT COLUMN: Drug Input & Selection (5 Cols) ────────────────── */}
          <div className="lg:col-span-5 space-y-6">
            <Card className="p-5">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                  <Search className="w-3.5 h-3.5 text-slate-500" />
                  <span>Search Medications</span>
                </h2>
                <span className="text-[11px] font-semibold text-slate-400">
                  {selectedDrugs.length}/10 Added
                </span>
              </div>

              {/* Debounced Autocomplete Search Bar */}
              <DrugSearchBar
                onSelectDrug={handleSelectDrug}
                disabled={isLoading}
                maxReached={isMaxReached}
              />

              {/* Preset Regimens */}
              <PresetSelector
                onSelectPreset={handleSelectPreset}
                className="mt-6 pt-5 border-t border-slate-100"
              />
            </Card>

            {/* Selected Drugs List */}
            <Card className="p-5">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                  <Pill className="w-3.5 h-3.5 text-sky-600" />
                  <span>Selected Regimen ({selectedDrugs.length})</span>
                </h3>
                {selectedDrugs.length > 0 && (
                  <button
                    type="button"
                    onClick={clearDrugs}
                    disabled={isLoading}
                    className="text-xs text-red-600 hover:text-red-800 font-medium flex items-center gap-1 cursor-pointer disabled:opacity-50"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Clear All</span>
                  </button>
                )}
              </div>

              {selectedDrugs.length === 0 ? (
                <EmptyState
                  title="No medications added"
                  description="Search a brand formulation above or choose a quick test regimen."
                />
              ) : (
                <div className="space-y-3">
                  <div className="flex flex-wrap gap-1.5 p-3 bg-slate-50 rounded-lg border border-slate-200 min-h-[64px]">
                    {selectedDrugs.map((drug, idx) => (
                      <DrugChip
                        key={`${drug}-${idx}`}
                        name={drug}
                        index={idx}
                        onRemove={removeDrug}
                        disabled={isLoading}
                      />
                    ))}
                  </div>

                  {error && <ErrorState message={error} className="mt-2" />}

                  <div className="pt-2">
                    <Button
                      variant="primary"
                      size="lg"
                      onClick={handleCheckInteractions}
                      disabled={isSubmitDisabled}
                      isLoading={isLoading}
                      className="w-full font-semibold shadow-xs"
                      rightIcon={!isLoading ? <ArrowRight className="w-4 h-4" /> : undefined}
                    >
                      {isLoading
                        ? "Evaluating Knowledge Graph..."
                        : `Check Interactions (${selectedDrugs.length} Drugs)`}
                    </Button>
                    {selectedDrugs.length < 2 && (
                      <p className="text-xs text-slate-400 text-center mt-2">
                        Add at least 2 medications to check all pairwise combinations.
                      </p>
                    )}
                  </div>
                </div>
              )}
            </Card>
          </div>

          {/* ── RIGHT COLUMN: Overview & Guide (7 Cols) ────────────────────── */}
          <div className="lg:col-span-7 space-y-6">
            <Card className="p-6">
              <h3 className="text-base font-bold text-slate-900 mb-2 flex items-center gap-2">
                <Info className="w-5 h-5 text-sky-600" />
                <span>How PharmaSafe-KG Analyzes Interactions</span>
              </h3>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed mb-4">
                When you click <strong>Check Interactions</strong>, the system executes a multi-stage
                pharmacological pipeline across all combinations:
              </p>

              <div className="space-y-3 text-xs sm:text-sm text-slate-700">
                <div className="p-3 bg-slate-50 rounded-md border border-slate-200">
                  <div className="font-semibold text-slate-900 mb-0.5">1. Brand-to-Generic Resolution</div>
                  <p className="text-xs text-slate-500">
                    Proprietary trade names are matched against 304k+ formulations in the Indian catalog,
                    extracting all active chemical entities.
                  </p>
                </div>

                <div className="p-3 bg-slate-50 rounded-md border border-slate-200">
                  <div className="font-semibold text-slate-900 mb-0.5">2. Knowledge Graph Traversal</div>
                  <p className="text-xs text-slate-500">
                    A single batched Cypher query searches Neo4j AuraDB for peer-reviewed DDI evidence,
                    ranking pairs into MAJOR, MODERATE, and MINOR severity.
                  </p>
                </div>

                <div className="p-3 bg-slate-50 rounded-md border border-slate-200">
                  <div className="font-semibold text-slate-900 mb-0.5">3. Inductive GNN Fallback</div>
                  <p className="text-xs text-slate-500">
                    If no documented evidence exists, our trained GraphSAGE model evaluates topological
                    neighborhood embeddings to predict potential undocumented interactions.
                  </p>
                </div>
              </div>
            </Card>

            <div className="p-4 bg-sky-50 rounded-lg border border-sky-200 text-xs text-sky-900 flex items-start gap-2.5">
              <ShieldCheck className="w-4 h-4 text-sky-600 shrink-0 mt-0.5" />
              <div className="leading-relaxed">
                <strong>Academic Research Architecture:</strong> GraphSAGE predictions are strictly separated
                from peer-reviewed Knowledge Graph facts. Non-documented combinations are marked as unassessed
                and never assumed safe.
              </div>
            </div>
          </div>
        </div>
      </PageContainer>
    </div>
  );
}
