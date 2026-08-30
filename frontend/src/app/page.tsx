"use client";

import React from "react";
import Link from "next/link";
import {
  Activity,
  ArrowRight,
  ShieldAlert,
  GitGraph,
  Sparkles,
  Database,
  CheckCircle2,
  FileCheck,
  Zap,
  BookOpen,
  Presentation,
  Layers,
} from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

export default function HomePage() {
  const metrics = [
    { label: "Total Graph Nodes", value: "50,073", subtext: "2,073 Ingredients + 48,000 Brands" },
    { label: "DDI Relationships", value: "89,367", subtext: "Calibrated Severity Evidence" },
    { label: "Mapped Indian Brands", value: "304,404", subtext: "1,002 Standardized Generics" },
    { label: "GraphSAGE Test AUC", value: "0.8834", subtext: "Leakage-Free Evaluation (N=21,325)" },
  ];

  const workflowSteps = [
    {
      step: "01",
      title: "Commercial Brand Input",
      desc: "Accepts 2–10 Indian brand or generic drug names (e.g. Combiflam, Ecosprin, Pantop 40).",
      icon: <Layers className="w-5 h-5 text-sky-600" />,
    },
    {
      step: "02",
      title: "Brand-to-Generic Resolution",
      desc: "Resolves trade names to active chemical entities with exact, alias, and fuzzy string distance matching.",
      icon: <FileCheck className="w-5 h-5 text-emerald-600" />,
    },
    {
      step: "03",
      title: "Knowledge Graph Traversal",
      desc: "Executes a single batched Cypher query against Neo4j AuraDB to extract documented clinical interactions.",
      icon: <Database className="w-5 h-5 text-blue-600" />,
    },
    {
      step: "04",
      title: "Inductive GNN Fallback",
      desc: "Evaluates unmapped drug pairs using a 3-layer GraphSAGE message-passing model for topological link prediction.",
      icon: <Sparkles className="w-5 h-5 text-purple-600" />,
    },
    {
      step: "05",
      title: "Explainable Clinical Output",
      desc: "Generates severity-ranked explanations with explicit separation of documented evidence vs AI predictions.",
      icon: <ShieldAlert className="w-5 h-5 text-amber-600" />,
    },
  ];

  const pillars = [
    {
      title: "Indian Brand-to-Generic Resolution",
      desc: "Maps over 304,000 commercial formulations to standardized INN generic entities. Resolves multi-ingredient fixed-dose combinations (e.g. Combiflam → ibuprofen + paracetamol).",
      badge: "304k+ Formulations",
      icon: <FileCheck className="w-6 h-6 text-sky-600" />,
    },
    {
      title: "Neo4j AuraDB Knowledge Graph",
      desc: "A production graph database indexing 50,073 nodes and 160,879 relationships. Stores calibrated severity tiers (Major 22.9%, Moderate 72.8%, Minor 4.3%) and pharmacological mechanism descriptions.",
      badge: "160k+ Relationships",
      icon: <Database className="w-6 h-6 text-emerald-600" />,
    },
    {
      title: "Inductive GraphSAGE Link Prediction",
      desc: "A 3-layer Graph Neural Network trained strictly on leakage-free train edge indices. Generalizes to unindexed drug combinations by aggregating local neighborhood topological embeddings.",
      badge: "AUC = 0.8834",
      icon: <GitGraph className="w-6 h-6 text-purple-600" />,
    },
    {
      title: "Epistemic AI Transparency",
      desc: "Maintains a strict clinical boundary between verified Knowledge Graph facts and statistical GNN predictions. Predicted pairs are clearly labeled with confidence percentages and unassessed severity.",
      badge: "Clinical Safety",
      icon: <ShieldAlert className="w-6 h-6 text-amber-600" />,
    },
  ];

  return (
    <div className="w-full pb-16">
      {/* ── HERO SECTION ──────────────────────────────────────────────────────── */}
      <div className="bg-white border-b border-slate-200 pt-12 pb-16">
        <PageContainer>
          <div className="max-w-3xl mx-auto text-center space-y-6">
            {/* Project Pill */}
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-50 border border-sky-200 text-sky-800 text-xs font-semibold select-none">
              <Activity className="w-3.5 h-3.5 text-sky-600" />
              <span>Final-Year Major Engineering Research Project</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight">
              Explainable Knowledge Graph + GNN for Drug Interaction Detection
            </h1>

            {/* Subtitle / Value Statement */}
            <p className="text-base sm:text-lg text-slate-600 leading-relaxed max-w-2xl mx-auto">
              Automated Indian brand-to-generic resolution, Neo4j Knowledge Graph traversal,
              and inductive GraphSAGE link prediction for multi-drug polypharmacy safety.
            </p>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
              <Link href="/analyze">
                <Button
                  size="lg"
                  variant="primary"
                  rightIcon={<ArrowRight className="w-4 h-4" />}
                  className="w-full sm:w-auto px-6 py-3 text-sm font-semibold shadow-sm"
                >
                  Analyze Medications
                </Button>
              </Link>
              <Link href="/demo">
                <Button
                  size="lg"
                  variant="demo"
                  leftIcon={<Presentation className="w-4 h-4" />}
                  className="w-full sm:w-auto px-6 py-3 text-sm font-semibold"
                >
                  Explore Defense Demo
                </Button>
              </Link>
              <Link href="/about">
                <Button
                  size="lg"
                  variant="outline"
                  leftIcon={<BookOpen className="w-4 h-4" />}
                  className="w-full sm:w-auto px-5 py-3 text-sm"
                >
                  Read Methodology
                </Button>
              </Link>
            </div>
          </div>
        </PageContainer>
      </div>

      {/* ── METRICS TICKER SECTION ────────────────────────────────────────────── */}
      <div className="bg-slate-100/70 border-b border-slate-200 py-6">
        <PageContainer>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {metrics.map((m, idx) => (
              <div
                key={idx}
                className="p-4 bg-white rounded-lg border border-slate-200 shadow-2xs text-center"
              >
                <div className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                  {m.value}
                </div>
                <div className="text-xs font-semibold text-slate-700 uppercase tracking-wider mt-1">
                  {m.label}
                </div>
                <div className="text-[11px] text-slate-400 mt-0.5">{m.subtext}</div>
              </div>
            ))}
          </div>
        </PageContainer>
      </div>

      {/* ── RESEARCH VALUE PILLARS ─────────────────────────────────────────────── */}
      <PageContainer>
        <div className="pt-16 pb-8 text-left">
          <div className="max-w-2xl mb-10">
            <Badge variant="sky" size="sm" className="mb-2">
              System Capabilities
            </Badge>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Bridging Commercial Indian Pharmacy & Pharmacological Science
            </h2>
            <p className="text-sm text-slate-600 mt-2 leading-relaxed">
              Standard clinical DDI tools only accept international chemical identifiers.
              PharmaSafe-KG bridges this gap by combining commercial retail catalogs with
              graph-structured pharmacology.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {pillars.map((p, idx) => (
              <Card key={idx} className="p-6 text-left flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-center">
                      {p.icon}
                    </div>
                    <Badge variant="neutral" size="sm">
                      {p.badge}
                    </Badge>
                  </div>
                  <h3 className="text-base font-bold text-slate-900 mb-2">{p.title}</h3>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">{p.desc}</p>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* ── SYSTEM PIPELINE WORKFLOW ────────────────────────────────────────── */}
        <div className="pt-16 pb-8 text-left">
          <div className="max-w-2xl mb-10">
            <Badge variant="neutral" size="sm" className="mb-2">
              Architecture & Execution
            </Badge>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              5-Step Polypharmacy Analysis Pipeline
            </h2>
            <p className="text-sm text-slate-600 mt-2 leading-relaxed">
              Every multi-drug query is processed through a deterministic multi-stage pipeline
              ensuring 100% evidentiary traceability.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {workflowSteps.map((ws, idx) => (
              <div
                key={idx}
                className="p-4 bg-white rounded-lg border border-slate-200 shadow-2xs flex flex-col justify-between text-left relative"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-bold text-slate-400 font-mono">{ws.step}</span>
                    <div className="p-1.5 rounded-md bg-slate-50 border border-slate-100">
                      {ws.icon}
                    </div>
                  </div>
                  <h4 className="text-sm font-semibold text-slate-900 mb-1.5">{ws.title}</h4>
                  <p className="text-xs text-slate-500 leading-relaxed">{ws.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── MODEL BENCHMARKS & VERIFIED METRICS TABLE ───────────────────────── */}
        <div className="pt-16 pb-8 text-left">
          <div className="max-w-2xl mb-8">
            <Badge variant="documented" size="sm" className="mb-2">
              Empirical Benchmarks
            </Badge>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Verified GNN Model Performance (Table 2)
            </h2>
            <p className="text-sm text-slate-600 mt-2 leading-relaxed">
              Models trained on 70% positive edges ($N=64,512$) and evaluated on the held-out
              test set ($N=21,325$) under strict leakage-free message-passing constraints.
            </p>
          </div>

          <div className="overflow-x-auto bg-white rounded-lg border border-slate-200 shadow-2xs">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-700 font-semibold uppercase tracking-wider text-[11px]">
                <tr>
                  <th className="py-3 px-4">Model Architecture</th>
                  <th className="py-3 px-4">Test ROC-AUC</th>
                  <th className="py-3 px-4">Test F1-Score</th>
                  <th className="py-3 px-4">Precision</th>
                  <th className="py-3 px-4">Recall</th>
                  <th className="py-3 px-4">Deployment Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                <tr className="bg-sky-50/40 font-medium">
                  <td className="py-3 px-4 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-sky-600" />
                    <strong>GraphSAGE (3-Layer Inductive)</strong>
                  </td>
                  <td className="py-3 px-4 font-mono font-bold text-sky-900">0.8834</td>
                  <td className="py-3 px-4 font-mono">0.8330</td>
                  <td className="py-3 px-4 font-mono">0.7215</td>
                  <td className="py-3 px-4 font-mono">0.9851</td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                      <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                      Active Runtime Model
                    </span>
                  </td>
                </tr>
                <tr>
                  <td className="py-3 px-4 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-slate-400" />
                    <span>Graph Attention Network (GAT, 4-Head)</span>
                  </td>
                  <td className="py-3 px-4 font-mono">0.8753</td>
                  <td className="py-3 px-4 font-mono">0.7867</td>
                  <td className="py-3 px-4 font-mono">0.6484</td>
                  <td className="py-3 px-4 font-mono">0.9999</td>
                  <td className="py-3 px-4">
                    <span className="text-[11px] text-slate-500 font-medium">
                      Baseline Comparison
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* ── PRESENTATION DEMO BANNER ────────────────────────────────────────── */}
        <div className="pt-8">
          <div className="p-6 sm:p-8 bg-indigo-50/80 rounded-xl border border-indigo-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 text-left">
            <div className="space-y-2 max-w-xl">
              <div className="inline-flex items-center gap-1.5 text-xs font-bold text-indigo-900 uppercase tracking-wider">
                <Presentation className="w-4 h-4 text-indigo-700" />
                <span>Academic Defense Presentation Mode</span>
              </div>
              <h3 className="text-xl font-bold text-slate-900">
                Evaluating Committee or Presentation Demo?
              </h3>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                Use the dedicated thesis presentation module to demonstrate pre-configured clinical
                scenarios (Warfarin bleed risk, cardiovascular polypharmacy, and AI link predictions)
                without requiring manual drug entry.
              </p>
            </div>
            <Link href="/demo" className="shrink-0">
              <Button
                variant="demo"
                size="md"
                rightIcon={<ArrowRight className="w-4 h-4" />}
                className="shadow-sm"
              >
                Launch Defense Mode
              </Button>
            </Link>
          </div>
        </div>
      </PageContainer>
    </div>
  );
}
