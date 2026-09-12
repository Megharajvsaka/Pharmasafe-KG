"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  ShieldCheck,
  Play,
  FlaskConical,
  Sparkles,
  ArrowRight,
  Pill,
  Loader2,
  Trash2,
  AlertTriangle,
  Info,
  Users,
  Database,
  Search,
  CheckCircle2,
  LogOut,
  RefreshCw,
  Building,
  Mail,
  Calendar,
  Layers,
  ExternalLink,
} from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { DrugSearchBar } from "@/components/drugs/DrugSearchBar";
import { DrugChip } from "@/components/drugs/DrugChip";
import { useAuth } from "@/context/AuthContext";
import { useAnalysis } from "@/context/AnalysisContext";
import { useToast } from "@/components/feedback/Toast";
import { api, AdminUserDTO, AdminStatsDTO } from "@/lib/api";

type AdminTab = "demo" | "drugs" | "users";

interface DemoPreset {
  id: string;
  title: string;
  subtitle: string;
  category: "Major Bleed Risk" | "Common Indian OTC" | "Metabolic Statin" | "Quad Polypharmacy";
  severityBadge: "MAJOR" | "MODERATE" | "AI PREDICTED";
  drugs: string[];
  expectedOutcome: string;
}

function AdminDashboardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tabParam = searchParams.get("tab") as AdminTab | null;

  const { user, isAuthenticated, isLoading: authLoading, logout } = useAuth();
  const { selectedDrugs, addDrug, removeDrug, clearDrugs, loadPreset, runAnalysis, isLoading: analysisLoading } =
    useAnalysis();
  const { showToast } = useToast();

  const [authorized, setAuthorized] = useState(false);
  const [activeTab, setActiveTab] = useState<AdminTab>(() => {
    if (tabParam && ["demo", "drugs", "users"].includes(tabParam)) {
      return tabParam;
    }
    return "demo";
  });

  const [executingPresetId, setExecutingPresetId] = useState<string | null>(null);
  const [adminUsers, setAdminUsers] = useState<AdminUserDTO[]>([]);
  const [adminStats, setAdminStats] = useState<AdminStatsDTO | null>(null);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [inspectedDrug, setInspectedDrug] = useState<string | null>("Combiflam");

  // ── STRICT ROLE-BASED ACCESS CONTROL GUARD ─────────────────────────────────
  useEffect(() => {
    if (!authLoading) {
      if (!isAuthenticated) {
        showToast({
          title: "Admin Sign In Required",
          description: "Please sign in with administrator credentials.",
          type: "error",
        });
        router.replace("/auth/login?redirect=/admin");
      } else if (user?.role !== "admin") {
        showToast({
          title: "Access Denied (403)",
          description: "You do not have administrator privileges to access this console.",
          type: "error",
        });
        router.replace("/dashboard");
      } else {
        setAuthorized(true);
      }
    }
  }, [authLoading, isAuthenticated, user, router, showToast]);

  // Sync tab with URL
  useEffect(() => {
    if (tabParam && ["demo", "drugs", "users"].includes(tabParam)) {
      setActiveTab(tabParam as AdminTab);
    }
  }, [tabParam]);

  const handleTabChange = (tab: AdminTab) => {
    setActiveTab(tab);
    router.replace(`/admin?tab=${tab}`, { scroll: false });
  };

  // Fetch admin data when switching to Users tab
  useEffect(() => {
    if (authorized && (activeTab === "users" || !adminStats)) {
      setLoadingUsers(true);
      Promise.all([api.getAdminUsers(), api.getAdminStats()])
        .then(([usersData, statsData]) => {
          setAdminUsers(usersData);
          setAdminStats(statsData);
        })
        .catch((err) => {
          showToast({
            title: "Admin Sync Failed",
            description: err?.detail || "Could not retrieve administrative directory.",
            type: "error",
          });
        })
        .finally(() => setLoadingUsers(false));
    }
  }, [authorized, activeTab, showToast]);

  const demoPresets: DemoPreset[] = [
    {
      id: "preset-1",
      title: "Combiflam + Ecosprin",
      subtitle: "Common Indian Fixed-Dose Combination + Antiplatelet",
      category: "Common Indian OTC",
      severityBadge: "MAJOR",
      drugs: ["Combiflam", "Ecosprin"],
      expectedOutcome:
        "Resolves Combiflam into Ibuprofen + Paracetamol. Flags Major additive gastrointestinal bleeding risk with Aspirin.",
    },
    {
      id: "preset-2",
      title: "Warfarin + Aspirin",
      subtitle: "Anticoagulant & NSAID Co-administration",
      category: "Major Bleed Risk",
      severityBadge: "MAJOR",
      drugs: ["Warfarin", "Aspirin"],
      expectedOutcome:
        "Critical clinical warning: Synergistic inhibition of coagulation pathway causing severe bleeding hazard.",
    },
    {
      id: "preset-3",
      title: "Atorvastatin + Clarithromycin",
      subtitle: "CYP3A4 Pharmacokinetic Metabolism Inhibition",
      category: "Metabolic Statin",
      severityBadge: "MAJOR",
      drugs: ["Atorvastatin", "Clarithromycin"],
      expectedOutcome:
        "Strong CYP3A4 inhibition elevates statin plasma concentration, precipitating hazardous rhabdomyolysis.",
    },
    {
      id: "preset-4",
      title: "4-Drug Cardiology & Diabetes Regimen",
      subtitle: "Combiflam + Ecosprin + Metformin + Pantop 40",
      category: "Quad Polypharmacy",
      severityBadge: "AI PREDICTED",
      drugs: ["Combiflam", "Ecosprin", "Metformin", "Pantop 40"],
      expectedOutcome:
        "Evaluates 6 pairwise combinations simultaneously, returning documented evidence and GraphSAGE AI predictions.",
    },
  ];

  const handleExecutePreset = async (preset: DemoPreset) => {
    setExecutingPresetId(preset.id);
    loadPreset(preset.drugs);

    showToast({
      title: "Loading Demo Preset",
      description: `Evaluating ${preset.drugs.join(" + ")} across dual verification engine...`,
      type: "info",
    });

    const result = await runAnalysis(preset.drugs);
    setExecutingPresetId(null);

    if (result) {
      router.push("/results");
    }
  };

  const handleCheckCustom = async () => {
    if (selectedDrugs.length < 2) {
      showToast({
        title: "Validation Error",
        description: "Please select at least 2 medications.",
        type: "error",
      });
      return;
    }
    const result = await runAnalysis();
    if (result) {
      router.push("/results");
    }
  };

  const handleLogout = () => {
    logout();
    showToast({
      title: "Signed Out",
      description: "You have been signed out of the administrative console.",
      type: "info",
    });
    router.push("/");
  };

  // ── BLOCK UNAUTHORIZED RENDERING ───────────────────────────────────────────
  if (authLoading || !authorized) {
    return (
      <div className="w-full min-h-[60vh] flex flex-col items-center justify-center text-center p-6 bg-slate-50">
        <div className="w-12 h-12 rounded-2xl bg-sky-50 border border-sky-200 flex items-center justify-center text-sky-600 mb-3 shadow-xs">
          <ShieldCheck className="w-6 h-6 animate-pulse" />
        </div>
        <p className="text-sm font-bold text-slate-800">Verifying Administrator Privileges...</p>
        <p className="text-xs text-slate-400 mt-1">Cryptographic session validation in progress.</p>
      </div>
    );
  }

  return (
    <div className="w-full min-h-[calc(100vh-140px)] bg-slate-50 py-6 px-4 sm:px-6 lg:px-8">
      <div className="flex flex-col md:flex-row gap-6 items-start">
        {/* ── LEFT SIDE PANEL (ADMIN NAVIGATION SIDEBAR) ───────────────────────── */}
        <aside className="w-full md:w-64 lg:w-72 bg-white rounded-2xl border border-slate-200 shadow-2xs shrink-0 flex flex-col justify-between p-5 min-h-[600px] md:sticky md:top-24">
          <div className="space-y-6 text-left">
            {/* Admin Profile Mini-Card */}
            <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 text-white">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-rose-600 text-white flex items-center justify-center font-bold text-sm shadow-xs">
                  {user?.avatarInitials || "AD"}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-bold truncate">{user?.name || "Administrator"}</p>
                  <div className="flex items-center gap-1.5 mt-0.5">
                    <span className="inline-block w-1.5 h-1.5 rounded-full bg-rose-400 animate-pulse" />
                    <span className="text-[11px] font-semibold text-rose-300 uppercase tracking-wider">
                      Role: Admin
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Navigation Items (3 Tabs: Demo, Drugs, Users — No Profile Tab) */}
            <nav className="space-y-1.5" aria-label="Admin Navigation">
              <button
                onClick={() => handleTabChange("demo")}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-semibold transition-colors text-left cursor-pointer ${
                  activeTab === "demo"
                    ? "bg-rose-50 text-rose-800 border border-rose-200 shadow-2xs"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`}
              >
                <Sparkles className="w-4 h-4 text-rose-600" />
                <span>Demo Workbench</span>
              </button>

              <button
                onClick={() => handleTabChange("drugs")}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-semibold transition-colors text-left cursor-pointer ${
                  activeTab === "drugs"
                    ? "bg-rose-50 text-rose-800 border border-rose-200 shadow-2xs"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`}
              >
                <Pill className="w-4 h-4 text-purple-600" />
                <span>Drugs Catalog</span>
              </button>

              <button
                onClick={() => handleTabChange("users")}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-semibold transition-colors text-left cursor-pointer ${
                  activeTab === "users"
                    ? "bg-rose-50 text-rose-800 border border-rose-200 shadow-2xs"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`}
              >
                <Users className="w-4 h-4 text-sky-600" />
                <span>Users Directory</span>
              </button>
            </nav>
          </div>

          {/* Bottom Controls */}
          <div className="pt-6 border-t border-slate-200 space-y-3">
            <div className="flex items-center gap-2 text-xs text-slate-500 px-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span className="font-semibold text-emerald-800">RBAC Verified</span>
            </div>

            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold text-red-600 hover:bg-red-50 transition-colors text-left cursor-pointer"
            >
              <LogOut className="w-4 h-4" />
              <span>Sign Out Console</span>
            </button>
          </div>
        </aside>

        {/* ── MAIN CONTENT AREA ─────────────────────────────────────────────────── */}
        <main className="flex-1 min-w-0 text-left">
          {/* TAB 1: DEMO WORKBENCH */}
          {activeTab === "demo" && (
            <div className="space-y-6">
              <div>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-rose-100 text-rose-800 font-bold text-xs uppercase tracking-wider">
                    Admin Portal
                  </span>
                  <span className="text-xs text-slate-400">•</span>
                  <span className="text-xs text-slate-500 font-medium">1-Click Fast Verification</span>
                </div>
                <h1 className="text-2xl font-bold text-slate-900 tracking-tight mt-1">
                  Clinical Demonstration Workbench
                </h1>
                <p className="text-xs sm:text-sm text-slate-500 mt-1">
                  Direct test cases pre-calibrated to showcase dual-engine resolution, GNN fallback, and severity triaging.
                </p>
              </div>

              {/* 1-Click Clinical Presets Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {demoPresets.map((preset) => (
                  <Card key={preset.id} className="p-5 flex flex-col justify-between hover:border-slate-300 transition-colors">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <Badge
                          variant={
                            preset.severityBadge === "MAJOR"
                              ? "major"
                              : preset.severityBadge === "MODERATE"
                              ? "moderate"
                              : "predicted"
                          }
                          size="sm"
                        >
                          {preset.severityBadge}
                        </Badge>
                        <span className="text-[11px] font-semibold text-slate-400">{preset.category}</span>
                      </div>

                      <h2 className="text-base font-bold text-slate-900">{preset.title}</h2>
                      <p className="text-xs text-slate-500 mt-0.5">{preset.subtitle}</p>

                      <div className="flex flex-wrap gap-1 mt-3">
                        {preset.drugs.map((drug, i) => (
                          <span
                            key={i}
                            className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-xs font-semibold"
                          >
                            {drug}
                          </span>
                        ))}
                      </div>

                      <div className="mt-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
                        <p className="text-xs text-slate-600 leading-relaxed">
                          <strong className="text-slate-800">Expected Outcome: </strong>
                          {preset.expectedOutcome}
                        </p>
                      </div>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-end">
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleExecutePreset(preset)}
                        disabled={executingPresetId === preset.id || analysisLoading}
                        className="font-semibold shadow-xs"
                        leftIcon={
                          executingPresetId === preset.id ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          ) : (
                            <Play className="w-3.5 h-3.5" />
                          )
                        }
                      >
                        {executingPresetId === preset.id ? "Analyzing..." : "Run Clinical Check"}
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>

              {/* Custom Ad-Hoc Analyzer */}
              <Card className="p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FlaskConical className="w-4 h-4 text-sky-600" />
                    <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                      Ad-Hoc Multi-Drug Evaluation
                    </h3>
                  </div>
                  <span className="text-xs font-semibold text-slate-400">{selectedDrugs.length}/10 Selected</span>
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

                {selectedDrugs.length > 0 && (
                  <div className="space-y-3 pt-2">
                    <div className="flex flex-wrap gap-1.5 p-3 bg-slate-50 rounded-lg border border-slate-200">
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

                    <div className="flex items-center justify-between pt-2">
                      <button
                        type="button"
                        onClick={clearDrugs}
                        className="text-xs text-red-600 hover:text-red-800 font-medium cursor-pointer"
                      >
                        Clear Selection
                      </button>

                      <Button
                        variant="primary"
                        size="md"
                        onClick={handleCheckCustom}
                        disabled={selectedDrugs.length < 2 || analysisLoading}
                        className="font-semibold shadow-xs"
                        rightIcon={<ArrowRight className="w-4 h-4" />}
                      >
                        {analysisLoading ? "Evaluating..." : `Check (${selectedDrugs.length} Drugs)`}
                      </Button>
                    </div>
                  </div>
                )}
              </Card>
            </div>
          )}

          {/* TAB 2: DRUGS CATALOG */}
          {activeTab === "drugs" && (
            <div className="space-y-6">
              <div>
                <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                  Pharmaceutical Catalog & Entity Decomposition
                </h1>
                <p className="text-xs sm:text-sm text-slate-500 mt-1">
                  Browse indexed commercial formulations, active generic mappings, and Knowledge Graph chemical nodes.
                </p>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card className="p-4">
                  <div className="text-2xl font-extrabold text-slate-900">225,449</div>
                  <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mt-1">
                    Brand-to-Generic Mappings
                  </div>
                </Card>

                <Card className="p-4">
                  <div className="text-2xl font-extrabold text-slate-900">304,404</div>
                  <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mt-1">
                    Indian Formulations Indexed
                  </div>
                </Card>

                <Card className="p-4">
                  <div className="text-2xl font-extrabold text-slate-900">1,761</div>
                  <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mt-1">
                    Generic Chemical Entities
                  </div>
                </Card>

                <Card className="p-4">
                  <div className="text-2xl font-extrabold text-slate-900">160,879</div>
                  <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mt-1">
                    Biomedical DDI Edges
                  </div>
                </Card>
              </div>

              {/* Live Drug Inspector */}
              <Card className="p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Search className="w-4 h-4 text-slate-500" />
                    <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                      Search Formulation or Generic
                    </h3>
                  </div>
                  <span className="text-xs text-slate-400">Type any Indian brand (e.g. Combiflam, Pantop)</span>
                </div>

                <DrugSearchBar
                  onSelectDrug={(name) => setInspectedDrug(name)}
                  placeholder="Search medication to inspect active chemical entities..."
                />

                {inspectedDrug && (
                  <div className="mt-4 p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                          Selected Medication
                        </span>
                        <h4 className="text-base font-bold text-slate-900">{inspectedDrug}</h4>
                      </div>
                      <Link href={`/drugs/${encodeURIComponent(inspectedDrug)}`}>
                        <Button variant="outline" size="sm" rightIcon={<ExternalLink className="w-3.5 h-3.5" />}>
                          View Full Monograph
                        </Button>
                      </Link>
                    </div>

                    <div className="pt-2 border-t border-slate-200">
                      <p className="text-xs text-slate-600">
                        This drug is registered in the PharmaSafe-KG catalog and indexed for dual-tier DDI evaluation.
                        Multi-ingredient brand formulations are dynamically decomposed into individual INN generic chemical entities.
                      </p>
                    </div>
                  </div>
                )}
              </Card>

              {/* Reference Drugs Quick List */}
              <Card className="p-6">
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3">
                  Reference Formulations for Quality Audits
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2.5">
                  {[
                    { name: "Combiflam", desc: "Ibuprofen + Paracetamol" },
                    { name: "Ecosprin", desc: "Aspirin" },
                    { name: "Warfarin", desc: "Coumarin Anticoagulant" },
                    { name: "Pantop 40", desc: "Pantoprazole" },
                    { name: "Metolar XR", desc: "Metoprolol" },
                    { name: "Atorva 10", desc: "Atorvastatin" },
                    { name: "Augmentin 625 Duo", desc: "Amoxicillin + Clavulanic" },
                    { name: "Telma H", desc: "Telmisartan + Hydrochlorothiazide" },
                  ].map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => setInspectedDrug(item.name)}
                      className="p-3 bg-white hover:bg-slate-50 rounded-lg border border-slate-200 text-left transition-colors cursor-pointer"
                    >
                      <p className="text-xs font-bold text-slate-900">{item.name}</p>
                      <p className="text-[11px] text-slate-500 mt-0.5 truncate">{item.desc}</p>
                    </button>
                  ))}
                </div>
              </Card>
            </div>
          )}

          {/* TAB 3: USERS DIRECTORY */}
          {activeTab === "users" && (
            <div className="space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                    User Management & Role Directory
                  </h1>
                  <p className="text-xs sm:text-sm text-slate-500 mt-1">
                    Registered accounts persisted in PostgreSQL with verified authentication and RBAC roles.
                  </p>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setLoadingUsers(true);
                    api.getAdminUsers().then(setAdminUsers).finally(() => setLoadingUsers(false));
                  }}
                  disabled={loadingUsers}
                  leftIcon={<RefreshCw className={`w-3.5 h-3.5 ${loadingUsers ? "animate-spin" : ""}`} />}
                >
                  Refresh Directory
                </Button>
              </div>

              {/* User Role Counts */}
              {adminStats && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <Card className="p-4">
                    <div className="text-2xl font-extrabold text-slate-900">{adminStats.total_users}</div>
                    <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mt-1">
                      Total Accounts
                    </div>
                  </Card>

                  <Card className="p-4">
                    <div className="text-2xl font-extrabold text-rose-600">
                      {adminStats.users_by_role["admin"] || 0}
                    </div>
                    <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mt-1">
                      Administrators
                    </div>
                  </Card>

                  <Card className="p-4">
                    <div className="text-2xl font-extrabold text-sky-600">
                      {(adminStats.users_by_role["clinician"] || 0) + (adminStats.users_by_role["researcher"] || 0)}
                    </div>
                    <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mt-1">
                      Clinicians / Researchers
                    </div>
                  </Card>

                  <Card className="p-4">
                    <div className="text-2xl font-extrabold text-emerald-600">
                      {adminStats.users_by_role["student"] || 0}
                    </div>
                    <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mt-1">
                      Students / Trainees
                    </div>
                  </Card>
                </div>
              )}

              {/* Users Table Card */}
              <Card className="overflow-hidden">
                <div className="p-4 border-b border-slate-200 flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                    PostgreSQL Registered Users ({adminUsers.length})
                  </span>
                  {loadingUsers && (
                    <span className="text-xs text-slate-400 flex items-center gap-1.5">
                      <Loader2 className="w-3.5 h-3.5 animate-spin text-sky-600" />
                      Loading...
                    </span>
                  )}
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider">
                        <th className="py-3 px-4">User</th>
                        <th className="py-3 px-4">Role</th>
                        <th className="py-3 px-4">Institution</th>
                        <th className="py-3 px-4">Status</th>
                        <th className="py-3 px-4">Registered</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {adminUsers.map((u) => (
                        <tr key={u.id} className="hover:bg-slate-50/80 transition-colors">
                          <td className="py-3 px-4">
                            <div className="font-bold text-slate-900">{u.full_name}</div>
                            <div className="text-[11px] text-slate-500">{u.email}</div>
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-2 py-0.5 rounded text-[11px] font-bold uppercase ${
                                u.role === "admin"
                                  ? "bg-rose-100 text-rose-800"
                                  : u.role === "clinician"
                                  ? "bg-sky-100 text-sky-800"
                                  : u.role === "researcher"
                                  ? "bg-purple-100 text-purple-800"
                                  : "bg-emerald-100 text-emerald-800"
                              }`}
                            >
                              {u.role}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-slate-600">{u.institution || "Independent"}</td>
                          <td className="py-3 px-4">
                            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700">
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                              Active
                            </span>
                          </td>
                          <td className="py-3 px-4 text-slate-500">
                            {u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default function AdminDemoPage() {
  return (
    <Suspense
      fallback={
        <div className="w-full min-h-[60vh] flex items-center justify-center">
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Loader2 className="w-5 h-5 animate-spin text-sky-600" />
            <span>Loading Administrative Console...</span>
          </div>
        </div>
      }
    >
      <AdminDashboardContent />
    </Suspense>
  );
}
