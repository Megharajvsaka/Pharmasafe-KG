"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import {
  LayoutDashboard,
  FlaskConical,
  Pill,
  User,
  LogOut,
  Search,
  Plus,
  Trash2,
  Play,
  RotateCcw,
  CheckCircle2,
  ShieldAlert,
  AlertTriangle,
  Clock,
  Bookmark,
  Building,
  ArrowRight,
  Database,
  Sparkles,
  Loader2,
  ShieldCheck,
  Info,
  Mail,
  Calendar,
} from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { DrugSearchBar } from "@/components/drugs/DrugSearchBar";
import { DrugChip } from "@/components/drugs/DrugChip";
import { EmptyState } from "@/components/feedback/EmptyState";
import { useAuth } from "@/context/AuthContext";
import { useAnalysis } from "@/context/AnalysisContext";
import { useToast } from "@/components/feedback/Toast";
import { api } from "@/lib/api";
import { HealthResponse } from "@/types/api";

type DashboardTab = "dashboard" | "analyse" | "single-drug" | "profile";

function DashboardContent() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading, logout } = useAuth();
  const {
    selectedDrugs,
    addDrug,
    removeDrug,
    clearDrugs,
    loadPreset,
    runAnalysis,
    recentAnalyses,
    savedRegimens,
    deleteSavedRegimen,
    clearRecentAnalyses,
    isLoading: analysisLoading,
  } = useAnalysis();
  const { showToast } = useToast();

  const searchParams = useSearchParams();
  const tabParam = searchParams.get("tab") as DashboardTab | null;

  const [activeTab, setActiveTab] = useState<DashboardTab>(() => {
    if (tabParam && ["dashboard", "analyse", "single-drug", "profile"].includes(tabParam)) {
      return tabParam;
    }
    return "dashboard";
  });

  useEffect(() => {
    if (tabParam && ["dashboard", "analyse", "single-drug", "profile"].includes(tabParam)) {
      setActiveTab(tabParam as DashboardTab);
    }
  }, [tabParam]);

  const handleTabChange = (tab: DashboardTab) => {
    setActiveTab(tab);
    router.replace(`/dashboard?tab=${tab}`, { scroll: false });
  };
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [singleDrugSearch, setSingleDrugSearch] = useState<string>("");

  useEffect(() => {
    if (!authLoading) {
      if (!isAuthenticated) {
        router.push("/auth/login?redirect=/dashboard");
      } else if (user?.role === "admin") {
        router.replace("/admin");
      }
    }
  }, [isAuthenticated, authLoading, user, router]);

  useEffect(() => {
    let isMounted = true;
    api
      .getHealth()
      .then((data) => {
        if (isMounted) setHealth(data);
      })
      .catch(() => {
        if (isMounted) setHealth(null);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const handleRunRecent = (drugs: string[]) => {
    loadPreset(drugs);
    showToast({
      title: "Regimen Loaded",
      description: `Loaded ${drugs.length} medications into workbench.`,
      type: "info",
    });
    handleTabChange("analyse");
  };

  const handleSelectSingleDrug = (drug: string) => {
    router.push(`/drugs/${encodeURIComponent(drug)}`);
  };

  const handleLogout = () => {
    logout();
    showToast({
      title: "Signed Out",
      description: "You have been logged out of the workstation.",
      type: "info",
    });
    router.push("/");
  };

  const handleCheckInteractions = async () => {
    if (selectedDrugs.length < 2) {
      showToast({
        title: "Validation Error",
        description: "Please select at least 2 medications to analyze interactions.",
        type: "error",
      });
      return;
    }

    const result = await runAnalysis();
    if (result) {
      router.push("/results");
    }
  };

  const popularDrugs = ["Combiflam", "Ecosprin", "Warfarin", "Pantop 40", "Metolar XR", "Atorva 10"];

  if (authLoading || !isAuthenticated) {
    return (
      <div className="w-full min-h-[60vh] flex items-center justify-center">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Loader2 className="w-5 h-5 animate-spin text-sky-600" />
          <span>Loading clinical workspace...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full min-h-[calc(100vh-140px)] bg-slate-50 py-6 px-4 sm:px-6 lg:px-8">
      <div className="flex flex-col md:flex-row gap-6 items-start">
        {/* ── LEFT SIDE PANEL (NAVIGATION SIDEBAR) ──────────────────────────────── */}
        <aside className="w-full md:w-64 lg:w-72 bg-white rounded-2xl border border-slate-200 shadow-2xs shrink-0 flex flex-col justify-between p-5 min-h-[600px] md:sticky md:top-24">
        <div className="space-y-6 text-left">
          {/* User Profile Mini-Card */}
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-sky-600 text-white flex items-center justify-center font-bold text-sm shadow-xs">
                {user?.avatarInitials || "MD"}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-bold text-slate-900 truncate">{user?.name}</p>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500" />
                  <span className="text-[11px] font-semibold text-slate-500 capitalize">{user?.role}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Navigation Items */}
          <nav className="space-y-1.5" aria-label="Workspace Navigation">
            <button
              onClick={() => handleTabChange("dashboard")}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-semibold transition-colors text-left cursor-pointer ${
                activeTab === "dashboard"
                  ? "bg-sky-50 text-sky-700 border border-sky-200 shadow-2xs"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              }`}
            >
              <LayoutDashboard className="w-4 h-4 text-sky-600" />
              <span>Dashboard</span>
            </button>

            <button
              onClick={() => handleTabChange("analyse")}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-semibold transition-colors text-left cursor-pointer ${
                activeTab === "analyse"
                  ? "bg-sky-50 text-sky-700 border border-sky-200 shadow-2xs"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              }`}
            >
              <FlaskConical className="w-4 h-4 text-emerald-600" />
              <span>Analyse</span>
            </button>

            <button
              onClick={() => handleTabChange("single-drug")}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-semibold transition-colors text-left cursor-pointer ${
                activeTab === "single-drug"
                  ? "bg-sky-50 text-sky-700 border border-sky-200 shadow-2xs"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              }`}
            >
              <Pill className="w-4 h-4 text-purple-600" />
              <span>Single Drug</span>
            </button>

            <button
              onClick={() => handleTabChange("profile")}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-semibold transition-colors text-left cursor-pointer ${
                activeTab === "profile"
                  ? "bg-sky-50 text-sky-700 border border-sky-200 shadow-2xs"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              }`}
            >
              <User className="w-4 h-4 text-slate-500" />
              <span>Profile</span>
            </button>
          </nav>
        </div>

        {/* Bottom Actions */}
        <div className="pt-6 border-t border-slate-200 space-y-3">
          {/* Live Status Badge */}
          <div className="flex items-center gap-2 text-xs text-slate-500 px-2">
            <span
              className={`w-2 h-2 rounded-full ${
                health?.status === "ok" ? "bg-emerald-500" : "bg-amber-500"
              }`}
            />
            <span className="truncate">
              {health?.status === "ok" ? "KG & GNN Online" : "Backend Offline"}
            </span>
          </div>

          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold text-red-600 hover:bg-red-50 transition-colors text-left cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out Workstation</span>
          </button>
        </div>
      </aside>

        {/* ── MAIN CONTENT AREA ─────────────────────────────────────────────────── */}
        <main className="flex-1 min-w-0 text-left">
        {/* TAB 1: DASHBOARD OVERVIEW */}
        {activeTab === "dashboard" && (
          <div className="space-y-8 max-w-5xl">
            <div>
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Clinical Dashboard</h1>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Overview of saved patient regimens, query history, and quick polypharmacy tools.
              </p>
            </div>

            {/* Quick Metrics Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Card className="p-4 flex items-center gap-3.5">
                <div className="w-10 h-10 rounded-lg bg-sky-50 border border-sky-200 flex items-center justify-center text-sky-600">
                  <Bookmark className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-slate-900">{savedRegimens.length}</div>
                  <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Saved Regimens</div>
                </div>
              </Card>

              <Card className="p-4 flex items-center gap-3.5">
                <div className="w-10 h-10 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600">
                  <Clock className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-slate-900">{recentAnalyses.length}</div>
                  <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Recent Analyses</div>
                </div>
              </Card>

              <Card className="p-4 flex items-center gap-3.5">
                <div className="w-10 h-10 rounded-lg bg-purple-50 border border-purple-200 flex items-center justify-center text-purple-600">
                  <Database className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-slate-900">50,073</div>
                  <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Graph Nodes</div>
                </div>
              </Card>
            </div>

            {/* Two Column Layout for Saved Regimens & Recent History */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Saved Regimens */}
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Bookmark className="w-4 h-4 text-sky-600" />
                    <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Saved Regimens</h2>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleTabChange("analyse")}
                    className="text-xs"
                    leftIcon={<Plus className="w-3 h-3" />}
                  >
                    New Regimen
                  </Button>
                </div>

                {savedRegimens.length === 0 ? (
                  <EmptyState
                    title="No saved regimens"
                    description="Run an analysis and save your frequent multi-drug combinations here."
                  />
                ) : (
                  <div className="space-y-3">
                    {savedRegimens.map((reg) => (
                      <div
                        key={reg.id}
                        className="p-3.5 rounded-lg border border-slate-200 bg-white hover:border-slate-300 transition-colors flex items-center justify-between gap-3"
                      >
                        <div>
                          <p className="text-sm font-semibold text-slate-900">{reg.name}</p>
                          <div className="flex flex-wrap gap-1 mt-1.5">
                            {reg.drugs.map((d, i) => (
                              <span
                                key={i}
                                className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[11px] font-medium"
                              >
                                {d}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <Button
                            size="sm"
                            variant="primary"
                            onClick={() => handleRunRecent(reg.drugs)}
                            className="text-xs px-2.5 py-1"
                            title="Load in workbench"
                          >
                            <Play className="w-3 h-3" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => deleteSavedRegimen(reg.id)}
                            className="text-xs text-red-600 hover:text-red-800 border-slate-200"
                            title="Delete regimen"
                          >
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </Card>

              {/* Recent Analyses History */}
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-emerald-600" />
                    <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Recent Analyses</h2>
                  </div>
                  {recentAnalyses.length > 0 && (
                    <button
                      onClick={clearRecentAnalyses}
                      className="text-xs text-slate-400 hover:text-slate-600 cursor-pointer"
                    >
                      Clear History
                    </button>
                  )}
                </div>

                {recentAnalyses.length === 0 ? (
                  <EmptyState
                    title="No recent analyses"
                    description="Analyses you execute will be logged here for quick reference."
                  />
                ) : (
                  <div className="space-y-3">
                    {recentAnalyses.slice(0, 5).map((item) => (
                      <div
                        key={item.id}
                        className="p-3.5 rounded-lg border border-slate-200 bg-white hover:border-slate-300 transition-colors flex items-center justify-between gap-3"
                      >
                        <div className="min-w-0">
                          <p className="text-xs font-semibold text-slate-900 truncate">
                            {item.drugs.join(" + ")}
                          </p>
                          <div className="flex items-center gap-2 mt-1 text-[11px] text-slate-500">
                            <span>{new Date(item.timestamp).toLocaleDateString()}</span>
                            <span>•</span>
                            <span className="font-semibold text-slate-700">
                              {item.totalFound} interaction(s)
                            </span>
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleRunRecent(item.drugs)}
                          className="text-xs px-2.5 py-1"
                        >
                          <RotateCcw className="w-3 h-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            </div>
          </div>
        )}

        {/* TAB 2: ANALYSE (IN-DASHBOARD WORKBENCH) */}
        {activeTab === "analyse" && (
          <div className="space-y-6">
            <div>
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Medication Interaction Workbench</h1>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Enter 2–10 commercial brand or generic medicines to evaluate polypharmacy interactions.
              </p>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
              {/* Left Column: Interactive Workbench (7 Cols) */}
              <div className="xl:col-span-7 space-y-6">
                <Card className="p-6 space-y-5">
                  <div className="flex items-center justify-between">
                    <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                      <Search className="w-3.5 h-3.5 text-slate-500" />
                      <span>Search Indian Medicines</span>
                    </h2>
                    <span className="text-xs font-semibold text-slate-400">
                      {selectedDrugs.length}/10 Added
                    </span>
                  </div>

                  <DrugSearchBar
                    onSelectDrug={(name) => {
                      const res = addDrug(name);
                      if (!res.success && res.reason) {
                        showToast({ title: "Cannot Add", description: res.reason, type: "error" });
                      }
                    }}
                    disabled={analysisLoading}
                    maxReached={selectedDrugs.length >= 10}
                  />

                  {/* Selected Chips */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                        Selected Combination ({selectedDrugs.length})
                      </span>
                      {selectedDrugs.length > 0 && (
                        <button
                          onClick={clearDrugs}
                          className="text-xs text-red-600 hover:text-red-800 cursor-pointer"
                        >
                          Clear All
                        </button>
                      )}
                    </div>

                    {selectedDrugs.length === 0 ? (
                      <div className="p-6 bg-slate-50 rounded-lg border border-dashed border-slate-300 text-center text-xs text-slate-400">
                        No drugs added yet. Use the search bar above to select medications.
                      </div>
                    ) : (
                      <div className="flex flex-wrap gap-2 p-3.5 bg-slate-50 rounded-lg border border-slate-200">
                        {selectedDrugs.map((drug, idx) => (
                          <DrugChip
                            key={`${drug}-${idx}`}
                            name={drug}
                            index={idx}
                            onRemove={removeDrug}
                            disabled={analysisLoading}
                          />
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Action Button */}
                  <div className="pt-3 border-t border-slate-100 flex items-center justify-end">
                    <Button
                      onClick={handleCheckInteractions}
                      disabled={selectedDrugs.length < 2 || selectedDrugs.length > 10 || analysisLoading}
                      variant="primary"
                      size="lg"
                      className="font-semibold shadow-xs"
                      rightIcon={
                        analysisLoading ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <ArrowRight className="w-4 h-4" />
                        )
                      }
                    >
                      {analysisLoading ? "Checking Knowledge Graph..." : "Analyze Interactions"}
                    </Button>
                  </div>
                </Card>
              </div>

              {/* Right Column: Engine Architecture & Guidelines (5 Cols) */}
              <div className="xl:col-span-5 space-y-6">
                {/* Dual-Engine DDI Detection Card */}
                <Card className="p-6">
                  <div className="flex items-center gap-2 mb-2">
                    <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0" />
                    <h3 className="text-base font-bold text-slate-900">Dual-Engine DDI Detection</h3>
                  </div>
                  <p className="text-xs text-slate-600 mb-4">
                    PharmaSafe-KG uses a two-tier clinical architecture to verify multi-drug safety:
                  </p>
                  <div className="space-y-3">
                    <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0" />
                        <span className="text-xs font-bold text-slate-900">Neo4j AuraDB Knowledge Graph</span>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed">
                        Evaluates pairs against 160,879 biomedical interactions with calibrated severity and documented mechanism explanations.
                      </p>
                    </div>
                    <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="w-2 h-2 rounded-full bg-purple-500 shrink-0" />
                        <span className="text-xs font-bold text-slate-900">Inductive GraphSAGE Link Prediction</span>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed">
                        Predicts unindexed combinations using local graph topological embeddings (ROC-AUC 0.8834).
                      </p>
                    </div>
                  </div>
                </Card>

                {/* Analysis Guidelines Card */}
                <Card className="p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <Info className="w-4 h-4 text-sky-600 shrink-0" />
                    <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Analysis Guidelines</h3>
                  </div>
                  <ul className="space-y-2.5 text-xs text-slate-600 leading-relaxed">
                    <li className="flex items-start gap-2">
                      <span className="text-slate-400 mt-0.5">•</span>
                      <span>
                        <strong className="text-slate-900 font-semibold">Fixed-Dose Combinations:</strong> Multi-ingredient brands (e.g. <em className="italic">Combiflam</em>) are automatically decomposed into active generic chemical entities.
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-slate-400 mt-0.5">•</span>
                      <span>
                        <strong className="text-slate-900 font-semibold">Pairwise Evaluation:</strong> Checking 3 medications evaluates 3 pairs; checking 4 medications evaluates 6 pairs simultaneously.
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-slate-400 mt-0.5">•</span>
                      <span>
                        <strong className="text-slate-900 font-semibold">Clinical Disclaimer:</strong> Absence of a documented interaction does not guarantee clinical safety.
                      </span>
                    </li>
                  </ul>
                </Card>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: SINGLE DRUG LOOKUP */}
        {activeTab === "single-drug" && (
          <div className="space-y-6 max-w-3xl">
            <div>
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Single Drug Monograph</h1>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Lookup any commercial brand or generic medicine to inspect active ingredients and known interactions.
              </p>
            </div>

            <Card className="p-6 space-y-4">
              <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <Search className="w-3.5 h-3.5 text-slate-500" />
                <span>Search Medicine</span>
              </h2>

              <DrugSearchBar
                onSelectDrug={handleSelectSingleDrug}
                disabled={false}
                placeholder="Type brand name (e.g. Combiflam, Pantop 40, Ecosprin)..."
              />

              <div className="pt-4 border-t border-slate-100">
                <p className="text-xs font-semibold text-slate-500 mb-2">Common clinical searches:</p>
                <div className="flex flex-wrap gap-2">
                  {popularDrugs.map((d) => (
                    <button
                      key={d}
                      onClick={() => handleSelectSingleDrug(d)}
                      className="px-2.5 py-1 rounded-md bg-slate-100 hover:bg-sky-50 hover:text-sky-700 text-xs font-medium text-slate-700 transition-colors cursor-pointer"
                    >
                      {d}
                    </button>
                  ))}
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* TAB 4: CLINICIAN PROFILE */}
        {activeTab === "profile" && (
          <div className="space-y-6 max-w-2xl">
            <div>
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Clinician Profile</h1>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Account information and institutional workstation credentials.
              </p>
            </div>

            <Card className="p-6 space-y-6">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-sky-600 text-white flex items-center justify-center text-xl font-bold shadow-sm">
                  {user?.avatarInitials || "MD"}
                </div>
                <div>
                  <h2 className="text-lg font-bold text-slate-900">{user?.name}</h2>
                  <p className="text-xs text-slate-500 capitalize">{user?.role} Account</p>
                </div>
              </div>

              <div className="divide-y divide-slate-100 text-sm">
                <div className="py-3 flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-500 uppercase flex items-center gap-1.5">
                    <Mail className="w-3.5 h-3.5 text-slate-400" />
                    <span>Email Address</span>
                  </span>
                  <span className="font-mono text-slate-900">{user?.email}</span>
                </div>

                <div className="py-3 flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-500 uppercase flex items-center gap-1.5">
                    <Building className="w-3.5 h-3.5 text-slate-400" />
                    <span>Institution / Hospital</span>
                  </span>
                  <span className="text-slate-900">{user?.institution || "Clinical Practice"}</span>
                </div>

                <div className="py-3 flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-500 uppercase flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-slate-400" />
                    <span>Account Role</span>
                  </span>
                  <Badge variant="sky" size="sm" className="capitalize">
                    {user?.role}
                  </Badge>
                </div>

                <div className="py-3 flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-500 uppercase flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    <span>Member Since</span>
                  </span>
                  <span className="text-slate-600">
                    {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : "Active"}
                  </span>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-100">
                <Button
                  onClick={handleLogout}
                  variant="outline"
                  size="md"
                  className="w-full text-red-600 hover:bg-red-50 border-red-200"
                  leftIcon={<LogOut className="w-4 h-4" />}
                >
                  Sign Out from Workstation
                </Button>
              </div>
            </Card>
          </div>
        )}
        </main>
      </div>
    </div>
  );
}


export default function DashboardPage() {
  return (
    <Suspense
      fallback={
        <div className="w-full min-h-[60vh] flex items-center justify-center">
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Loader2 className="w-5 h-5 animate-spin text-sky-600" />
            <span>Loading clinical workspace...</span>
          </div>
        </div>
      }
    >
      <DashboardContent />
    </Suspense>
  );
}
