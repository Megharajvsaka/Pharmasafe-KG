"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  FileText,
  ArrowLeft,
  RefreshCw,
  Printer,
  ShieldAlert,
  AlertTriangle,
  Info,
  Sparkles,
  Database,
  Pill,
  GitGraph,
  CheckCircle2,
  ExternalLink,
} from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Tabs } from "@/components/ui/Tabs";
import { EmptyState } from "@/components/feedback/EmptyState";
import { ResultsSummaryBanner } from "@/components/interactions/ResultsSummaryBanner";
import { InteractionCard } from "@/components/interactions/InteractionCard";
import { SafePairCard } from "@/components/interactions/SafePairCard";
import { ResolvedDrugsTable } from "@/components/interactions/ResolvedDrugsTable";
import { InteractionGraph } from "@/components/graph/InteractionGraph";
import { useAnalysis } from "@/context/AnalysisContext";
import { useAuth } from "@/context/AuthContext";

export default function ResultsPage() {
  const router = useRouter();
  const { user } = useAuth();
  const { selectedDrugs, checkResult, resetAnalysis, clearDrugs } = useAnalysis();
  const [activeTab, setActiveTab] = useState<string>("all");

  const workbenchUrl = user?.role === "admin" ? "/admin?tab=demo" : "/dashboard?tab=analyse";

  // Handle direct navigation with no analysis data
  if (!checkResult || !checkResult.brand_names || checkResult.brand_names.length === 0) {
    return (
      <div className="w-full pb-16">
        <div className="bg-white border-b border-slate-200 py-6">
          <PageContainer>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900">
              Polypharmacy Analysis Results
            </h1>
          </PageContainer>
        </div>

        <PageContainer className="pt-12 max-w-2xl">
          <EmptyState
            title="No Active Analysis Available"
            description="You have not evaluated any drug combinations yet, or your session has expired. Start by selecting medications on the workbench."
            action={
              <Link href={workbenchUrl}>
                <Button variant="primary" size="md">
                  Start New Analysis
                </Button>
              </Link>
            }
          />
        </PageContainer>
      </div>
    );
  }

  const {
    interactions = [],
    safe_pairs_detail = [],
    resolved_drugs = [],
    total_drugs,
    pairs_checked,
  } = checkResult;

  const majorInteractions = interactions.filter((i) => i.severity === "MAJOR");
  const moderateInteractions = interactions.filter((i) => i.severity === "MODERATE");
  const minorInteractions = interactions.filter((i) => i.severity === "MINOR");
  const predictedInteractions = interactions.filter(
    (i) => i.status === "predicted" || i.source === "gnn_predicted"
  );
  const documentedInteractions = interactions.filter(
    (i) => i.status === "documented" && i.source === "knowledge_graph"
  );

  const tabs = [
    { id: "all", label: "All Findings", count: interactions.length + safe_pairs_detail.length },
    {
      id: "major",
      label: "Critical (Major)",
      count: majorInteractions.length,
      icon: <ShieldAlert className="w-3.5 h-3.5 text-red-600" />,
    },
    {
      id: "documented",
      label: "Documented Evidence",
      count: documentedInteractions.length,
      icon: <Database className="w-3.5 h-3.5 text-emerald-600" />,
    },
    {
      id: "predicted",
      label: "AI Predicted",
      count: predictedInteractions.length,
      icon: <Sparkles className="w-3.5 h-3.5 text-purple-600" />,
    },
    {
      id: "safe",
      label: "No Documented DDI",
      count: safe_pairs_detail.length,
    },
  ];

  const handlePrint = () => {
    window.print();
  };

  const handleNewAnalysis = () => {
    resetAnalysis();
    clearDrugs();
    router.push(workbenchUrl);
  };

  return (
    <div className="w-full pb-16 text-left">
      {/* Top Header Bar */}
      <div className="bg-white border-b border-slate-200 py-6 print:hidden">
        <PageContainer>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-sky-600 flex items-center justify-center text-white">
                  <FileText className="w-4 h-4" />
                </div>
                <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                  Polypharmacy Interaction Report
                </h1>
              </div>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Combinatorial analysis for {total_drugs} medications across {pairs_checked} evaluated pairs.
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center flex-wrap gap-2">
              <Link href={workbenchUrl}>
                <Button
                  variant="outline"
                  size="sm"
                  leftIcon={<ArrowLeft className="w-3.5 h-3.5" />}
                >
                  Modify Drugs
                </Button>
              </Link>
              <Button
                variant="outline"
                size="sm"
                onClick={handlePrint}
                leftIcon={<Printer className="w-3.5 h-3.5" />}
              >
                Print Report
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={handleNewAnalysis}
                leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
              >
                New Analysis
              </Button>
            </div>
          </div>
        </PageContainer>
      </div>

      <PageContainer className="pt-8 space-y-8">
        {/* ── 1. Statistical Summary Banner ─────────────────────────────────── */}
        <ResultsSummaryBanner result={checkResult} />

        {/* ── 2. Filter Tabs ────────────────────────────────────────────────── */}
        <div className="print:hidden">
          <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />
        </div>

        {/* ── 3. Grouped Findings ───────────────────────────────────────────── */}
        <div className="space-y-6">
          {/* Group 1: Major Interactions */}
          {(activeTab === "all" || activeTab === "major") && majorInteractions.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-bold text-red-900 uppercase tracking-wider flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-red-600" />
                  <span>Critical Risk (Major Severity) — {majorInteractions.length}</span>
                </h2>
                <span className="text-xs text-red-700 font-medium">Immediate Clinical Attention</span>
              </div>
              <div className="space-y-3">
                {majorInteractions.map((interaction, idx) => (
                  <InteractionCard key={`major-${idx}`} interaction={interaction} />
                ))}
              </div>
            </div>
          )}

          {/* Group 2: Moderate Interactions */}
          {(activeTab === "all" || activeTab === "documented") && moderateInteractions.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-bold text-amber-900 uppercase tracking-wider flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  <span>Moderate Risk Interactions — {moderateInteractions.length}</span>
                </h2>
                <span className="text-xs text-amber-700 font-medium">Monitoring Advised</span>
              </div>
              <div className="space-y-3">
                {moderateInteractions.map((interaction, idx) => (
                  <InteractionCard key={`mod-${idx}`} interaction={interaction} />
                ))}
              </div>
            </div>
          )}

          {/* Group 3: Minor Interactions */}
          {(activeTab === "all" || activeTab === "documented") && minorInteractions.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-bold text-emerald-900 uppercase tracking-wider flex items-center gap-2">
                  <Info className="w-4 h-4 text-emerald-600" />
                  <span>Minor Interactions — {minorInteractions.length}</span>
                </h2>
                <span className="text-xs text-emerald-700 font-medium">Low Clinical Impact</span>
              </div>
              <div className="space-y-3">
                {minorInteractions.map((interaction, idx) => (
                  <InteractionCard key={`min-${idx}`} interaction={interaction} />
                ))}
              </div>
            </div>
          )}

          {/* Group 4: AI Predictions */}
          {(activeTab === "all" || activeTab === "predicted") && predictedInteractions.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-bold text-purple-900 uppercase tracking-wider flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-purple-600" />
                  <span>AI Predicted Interactions (GraphSAGE) — {predictedInteractions.length}</span>
                </h2>
                <span className="text-xs text-purple-700 font-medium font-mono">
                  Confidence $\ge$ 70%
                </span>
              </div>
              <div className="space-y-3">
                {predictedInteractions.map((interaction, idx) => (
                  <InteractionCard key={`pred-${idx}`} interaction={interaction} />
                ))}
              </div>
            </div>
          )}

          {/* Group 5: Non-Interacting Combinations */}
          {(activeTab === "all" || activeTab === "safe") && safe_pairs_detail.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-bold text-slate-700 uppercase tracking-wider flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-slate-500" />
                  <span>Combinations With No Documented DDI — {safe_pairs_detail.length}</span>
                </h2>
                <span className="text-xs text-slate-500">Unassessed in Knowledge Base</span>
              </div>
              <div className="space-y-2">
                {safe_pairs_detail.map((pair, idx) => (
                  <SafePairCard key={`safe-${idx}`} pair={pair} />
                ))}
              </div>
            </div>
          )}

          {/* Empty Tab State */}
          {activeTab === "major" && majorInteractions.length === 0 && (
            <Card className="p-8 text-center bg-white">
              <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
              <h3 className="text-sm font-bold text-slate-800">No Major Risk Interactions</h3>
              <p className="text-xs text-slate-500 mt-1">
                No high-severity interactions were detected among the selected medications.
              </p>
            </Card>
          )}

          {activeTab === "predicted" && predictedInteractions.length === 0 && (
            <Card className="p-8 text-center bg-white">
              <Info className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <h3 className="text-sm font-bold text-slate-800">No GNN Predictions</h3>
              <p className="text-xs text-slate-500 mt-1">
                All pairwise combinations were either resolved through direct Knowledge Graph evidence
                or fell below the 70% prediction confidence threshold.
              </p>
            </Card>
          )}
        </div>

        {/* ── 4. Brand-to-Generic Resolution Lineage ────────────────────────── */}
        <ResolvedDrugsTable resolvedDrugs={resolved_drugs} />

        {/* ── 5. Subgraph Topology Visualization ────────────────────────────── */}
        <div className="space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <GitGraph className="w-4 h-4 text-sky-600" />
              <span>Interactive Subgraph Topology</span>
            </h2>
            <Link
              href={`/graph?${selectedDrugs.map((d) => `drugs=${encodeURIComponent(d)}`).join("&")}`}
            >
              <Button
                variant="outline"
                size="sm"
                className="text-xs"
                rightIcon={<ExternalLink className="w-3.5 h-3.5" />}
              >
                Open Full Knowledge Graph Explorer
              </Button>
            </Link>
          </div>
          <InteractionGraph drugs={selectedDrugs} height={400} />
        </div>

        {/* ── 6. Clinical & Academic Disclaimer ─────────────────────────────── */}
        <div className="p-4 bg-slate-100/70 rounded-lg border border-slate-200 text-xs text-slate-600 leading-relaxed">
          <p>
            <strong className="font-semibold text-slate-900">Clinical Decision Support Disclaimer:</strong>{" "}
            PharmaSafe-KG is an academic pair-interaction reasoning system. Documented interaction mechanisms
            are grounded in DrugBank and clinical literature. GNN predictions represent topological link
            probabilities and should be verified experimentally before clinical adoption.
          </p>
        </div>
      </PageContainer>
    </div>
  );
}
