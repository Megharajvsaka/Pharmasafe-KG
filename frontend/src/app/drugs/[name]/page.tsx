"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  Pill,
  ShieldAlert,
  AlertTriangle,
  Info,
  ArrowLeft,
  FlaskConical,
  GitGraph,
  ExternalLink,
  BookOpen,
  Database,
  RefreshCw,
  Search,
  CheckCircle2,
} from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Tabs } from "@/components/ui/Tabs";
import { Skeleton } from "@/components/feedback/Skeleton";
import { ErrorState } from "@/components/feedback/ErrorState";
import { EmptyState } from "@/components/feedback/EmptyState";
import { api, ApiClientError } from "@/lib/api";
import { DrugInfoResponse, DrugInteractionItem } from "@/types/api";
import { useAnalysis } from "@/context/AnalysisContext";

export default function DrugMonographPage() {
  const params = useParams();
  const router = useRouter();
  const { addDrug } = useAnalysis();

  const rawName = params?.name ? String(params.name) : "";
  const decodedDrugName = decodeURIComponent(rawName);

  const [drugInfo, setDrugInfo] = useState<DrugInfoResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<string>("all");

  const fetchDrugDetails = async () => {
    if (!decodedDrugName) {
      setNotFound(true);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    setNotFound(false);

    try {
      const data = await api.getDrugInfo(decodedDrugName);
      setDrugInfo(data);
    } catch (err) {
      if (err instanceof ApiClientError && err.status === 404) {
        setNotFound(true);
      } else {
        const msg =
          err instanceof ApiClientError
            ? err.detail
            : "Failed to retrieve drug monograph from PharmaSafe-KG.";
        setError(msg);
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDrugDetails();
  }, [decodedDrugName]);

  const handleAnalyzeWithOthers = () => {
    if (drugInfo?.brand_name) {
      addDrug(drugInfo.brand_name);
      router.push("/analyze");
    }
  };

  // ── Loading Skeleton ────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="w-full pb-16 text-left">
        <div className="bg-white border-b border-slate-200 py-6">
          <PageContainer>
            <Skeleton className="h-4 w-48 mb-3" />
            <div className="flex items-center gap-3">
              <Skeleton className="h-10 w-10 rounded-lg" />
              <div>
                <Skeleton className="h-7 w-64 mb-1" />
                <Skeleton className="h-4 w-40" />
              </div>
            </div>
          </PageContainer>
        </div>

        <PageContainer className="pt-8 space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-20 rounded-lg" />
            ))}
          </div>
          <Skeleton className="h-40 rounded-lg" />
          <Skeleton className="h-64 rounded-lg" />
        </PageContainer>
      </div>
    );
  }

  // ── Not Found State (404) ───────────────────────────────────────────────────
  if (notFound) {
    return (
      <div className="w-full pb-16 text-left">
        <div className="bg-white border-b border-slate-200 py-6">
          <PageContainer>
            <Breadcrumbs
              items={[
                { label: "Medication Workbench", href: "/analyze" },
                { label: "Drug Not Found" },
              ]}
            />
          </PageContainer>
        </div>

        <PageContainer className="pt-12 max-w-xl">
          <EmptyState
            title={`Medication "${decodedDrugName}" Not Found`}
            description="The requested commercial brand or formulation is not present in the indexed Indian pharmaceutical catalog (304,404 formulations). Please verify spelling or search by generic chemical name."
            action={
              <div className="flex gap-3 justify-center">
                <Link href="/dashboard?tab=analyse">
                  <Button variant="primary" size="md" leftIcon={<Search className="w-4 h-4" />}>
                    Search Medication Catalog
                  </Button>
                </Link>
                <Link href="/dashboard?tab=analyse">
                  <Button variant="outline" size="md" leftIcon={<ArrowLeft className="w-4 h-4" />}>
                    Back to Workbench
                  </Button>
                </Link>
              </div>
            }
          />
        </PageContainer>
      </div>
    );
  }

  // ── Backend Error State ─────────────────────────────────────────────────────
  if (error || !drugInfo) {
    return (
      <div className="w-full pb-16 text-left">
        <div className="bg-white border-b border-slate-200 py-6">
          <PageContainer>
            <Breadcrumbs
              items={[
                { label: "Medication Workbench", href: "/analyze" },
                { label: "Monograph Error" },
              ]}
            />
          </PageContainer>
        </div>

        <PageContainer className="pt-12 max-w-xl">
          <ErrorState
            title="Unable to Retrieve Drug Monograph"
            message={error || "Could not connect to the PharmaSafe-KG knowledge base."}
            onRetry={fetchDrugDetails}
          />
        </PageContainer>
      </div>
    );
  }

  const {
    brand_name,
    generics = [],
    total_known_ddis,
    major_count,
    moderate_count,
    minor_count,
    interactions = [],
  } = drugInfo;

  const majorList = interactions.filter((i) => i.severity === "MAJOR");
  const moderateList = interactions.filter((i) => i.severity === "MODERATE");
  const minorList = interactions.filter((i) => i.severity === "MINOR");

  const tabs = [
    { id: "all", label: "All Known DDIs", count: interactions.length },
    {
      id: "major",
      label: "Critical (Major)",
      count: major_count,
      icon: <ShieldAlert className="w-3.5 h-3.5 text-red-600" />,
    },
    {
      id: "moderate",
      label: "Moderate Risk",
      count: moderate_count,
      icon: <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />,
    },
    {
      id: "minor",
      label: "Minor Impact",
      count: minor_count,
      icon: <Info className="w-3.5 h-3.5 text-emerald-600" />,
    },
  ];

  let displayedInteractions = interactions;
  if (activeTab === "major") displayedInteractions = majorList;
  else if (activeTab === "moderate") displayedInteractions = moderateList;
  else if (activeTab === "minor") displayedInteractions = minorList;

  return (
    <div className="w-full pb-16 text-left">
      {/* ── Top Header Bar ───────────────────────────────────────────────────── */}
      <div className="bg-white border-b border-slate-200 py-6">
        <PageContainer>
          <Breadcrumbs
            items={[
              { label: "Medication Workbench", href: "/analyze" },
              { label: "Drug Monographs" },
              { label: brand_name },
            ]}
            className="mb-2"
          />

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-lg bg-sky-600 flex items-center justify-center text-white shrink-0 mt-0.5">
                <Pill className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2.5 flex-wrap">
                  <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                    {brand_name}
                  </h1>
                  <Badge variant="sky" size="sm">
                    Commercial Formulation
                  </Badge>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-slate-500 mt-1 flex-wrap">
                  <span className="font-semibold text-slate-700">Active Generic Chemical(s):</span>
                  {generics.map((g, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 bg-slate-100 border border-slate-200 rounded font-mono text-[11px] text-slate-800"
                    >
                      {g}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="flex items-center flex-wrap gap-2">
              <Button
                variant="primary"
                size="sm"
                onClick={handleAnalyzeWithOthers}
                leftIcon={<FlaskConical className="w-4 h-4" />}
              >
                Analyze with other drugs
              </Button>
              <Link href={`/graph?drugs=${encodeURIComponent(brand_name)}&drugs=Ecosprin`}>
                <Button
                  variant="outline"
                  size="sm"
                  leftIcon={<GitGraph className="w-4 h-4 text-sky-600" />}
                >
                  Explore in Graph
                </Button>
              </Link>
            </div>
          </div>
        </PageContainer>
      </div>

      <PageContainer className="pt-8 space-y-8">
        {/* ── Section 1: Statistical Summary Tiles ─────────────────────────── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-4 bg-white rounded-lg border border-slate-200 shadow-2xs text-center">
            <div className="text-2xl font-bold text-slate-900">{total_known_ddis}</div>
            <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mt-0.5">
              Total Documented DDIs
            </div>
          </div>

          <div className="p-4 bg-red-50/70 rounded-lg border border-red-200 text-center">
            <div className="text-2xl font-bold text-red-700">{major_count}</div>
            <div className="text-[11px] font-semibold text-red-900 uppercase tracking-wider mt-0.5">
              Major Severity
            </div>
          </div>

          <div className="p-4 bg-amber-50/70 rounded-lg border border-amber-200 text-center">
            <div className="text-2xl font-bold text-amber-700">{moderate_count}</div>
            <div className="text-[11px] font-semibold text-amber-900 uppercase tracking-wider mt-0.5">
              Moderate Severity
            </div>
          </div>

          <div className="p-4 bg-emerald-50/70 rounded-lg border border-emerald-200 text-center">
            <div className="text-2xl font-bold text-emerald-700">{minor_count}</div>
            <div className="text-[11px] font-semibold text-emerald-900 uppercase tracking-wider mt-0.5">
              Minor Severity
            </div>
          </div>
        </div>

        {/* ── Section 2: Active Generic Ingredient Breakdown ────────────────── */}
        <Card className="p-5">
          <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center gap-2">
            <Database className="w-4 h-4 text-sky-600" />
            <span>Formulation Profile & Composition ({generics.length} Ingredients)</span>
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {generics.map((generic, idx) => (
              <div
                key={idx}
                className="p-3.5 bg-slate-50 rounded-lg border border-slate-200 flex items-start justify-between gap-3"
              >
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                    <h3 className="text-sm font-bold text-slate-900 capitalize">{generic}</h3>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    Indexed DrugBank generic entity with verified interaction topology.
                  </p>
                </div>
                <span className="text-[10px] font-mono font-semibold bg-white px-2 py-0.5 rounded border border-slate-200 text-slate-600 shrink-0">
                  Active Entity #{idx + 1}
                </span>
              </div>
            ))}
          </div>
        </Card>

        {/* ── Section 3: Known Interactions Feed ────────────────────────────── */}
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-sky-600" />
                <span>Documented Knowledge Graph Interactions</span>
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Peer-reviewed interactions indexed in Neo4j AuraDB for the active ingredients of {brand_name}.
              </p>
            </div>
          </div>

          {interactions.length > 0 && (
            <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />
          )}

          {displayedInteractions.length === 0 ? (
            <Card className="p-8 text-center bg-slate-50/60 border-slate-200">
              <Info className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <Badge variant="safe" size="md" className="mb-2">
                No Documented DDI
              </Badge>
              <h3 className="text-sm font-bold text-slate-800">
                No Documented Interactions for Selected Filter
              </h3>
              <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                No peer-reviewed interactions were indexed under this severity level. (Note: Lack of
                documented evidence in knowledge bases does not guarantee clinical safety.)
              </p>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {displayedInteractions.map((item, idx) => {
                const targetName = String(item.target_generic || item.interacting_ingredient || "Unknown Drug");
                const sourceName = String(item.source_generic || generics[0] || brand_name);
                const sev = (item.severity?.toUpperCase() || "MODERATE") as "MAJOR" | "MODERATE" | "MINOR";

                const isMajor = sev === "MAJOR";
                const isModerate = sev === "MODERATE";

                return (
                  <Card
                    key={idx}
                    accent={isMajor ? "major" : isModerate ? "moderate" : "minor"}
                    className="p-4 space-y-2.5 text-left"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-1.5 font-bold text-slate-900 text-xs sm:text-sm">
                        <span className="capitalize">{sourceName}</span>
                        <span className="text-slate-400">↔</span>
                        <span className="capitalize text-sky-700">{targetName}</span>
                      </div>
                      <Badge severity={sev} size="sm">
                        {sev}
                      </Badge>
                    </div>

                    {item.mechanism && (
                      <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-2.5 rounded border border-slate-100">
                        {item.mechanism}
                      </p>
                    )}

                    <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-100">
                      <span className="flex items-center gap-1">
                        <Database className="w-3 h-3 text-emerald-600" />
                        <span>Source: DrugBank Knowledge Graph</span>
                      </span>
                      <Link
                        href={`/drugs/${encodeURIComponent(targetName)}`}
                        className="text-sky-600 hover:text-sky-800 font-semibold flex items-center gap-0.5"
                      >
                        <span>Inspect {targetName}</span>
                        <ExternalLink className="w-2.5 h-2.5" />
                      </Link>
                    </div>
                  </Card>
                );
              })}
            </div>
          )}
        </div>

        {/* ── Section 4: Clinical Disclaimer ────────────────────────────────── */}
        <div className="p-4 bg-slate-100/70 rounded-lg border border-slate-200 text-xs text-slate-600 leading-relaxed">
          <strong className="font-semibold text-slate-900">Research & Clinical Decision Support Notice:</strong>{" "}
          Data shown on this monograph is derived from PharmaSafe-KG&apos;s Knowledge Graph mapping of DrugBank
          and Indian commercial catalogs. Documented interactions reflect indexed monographs; absence of an
          interaction record does not guarantee clinical safety in polypharmacy regimens.
        </div>
      </PageContainer>
    </div>
  );
}
