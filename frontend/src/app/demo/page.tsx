"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Presentation,
  Play,
  ShieldAlert,
  GitGraph,
  Sparkles,
  Database,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  Info,
} from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

interface DemoScenario {
  id: string;
  title: string;
  category: string;
  drugs: string[];
  clinicalFocus: string;
  expectedFindings: {
    documentedMajor: number;
    documentedModerate: number;
    predicted: number;
    safe: number;
  };
  narrative: string;
}

export default function DemoPage() {
  const scenarios: DemoScenario[] = [
    {
      id: "warfarin",
      title: "Scenario 1: Warfarin Hemorrhage Risk",
      category: "High-Risk Anticoagulation",
      drugs: ["Warfarin", "Combiflam", "Pantop 40"],
      clinicalFocus:
        "Combiflam contains Ibuprofen + Paracetamol. Ibuprofen + Warfarin triggers a MAJOR gastrointestinal bleeding warning via COX-1 inhibition and platelet displacement.",
      expectedFindings: {
        documentedMajor: 1,
        documentedModerate: 1,
        predicted: 0,
        safe: 1,
      },
      narrative:
        "Demonstrates automatic fixed-dose combination resolution (Combiflam → ibuprofen + paracetamol) and high-severity clinical warning extraction.",
    },
    {
      id: "cardiac",
      title: "Scenario 2: Cardiovascular Polypharmacy",
      category: "Cardiology Combination",
      drugs: ["Atorva 10", "Ecosprin", "Metolar XR"],
      clinicalFocus:
        "Atorvastatin + Aspirin + Metoprolol. Tests standard triple therapy for ischemic heart disease with moderate CYP3A4 and bleeding considerations.",
      expectedFindings: {
        documentedMajor: 0,
        documentedModerate: 2,
        predicted: 0,
        safe: 1,
      },
      narrative:
        "Demonstrates multi-drug interaction checking with moderate severity ranking and pharmacological mechanism descriptions.",
    },
    {
      id: "ai_prediction",
      title: "Scenario 3: Inductive GNN Link Prediction",
      category: "AI Link Discovery",
      drugs: ["Metformin 500", "Glibenclamide", "Ecosprin"],
      clinicalFocus:
        "Evaluates dual secretagogue/biguanide diabetes regimen against antiplatelet therapy, highlighting GNN topological link predictions with confidence scores.",
      expectedFindings: {
        documentedMajor: 0,
        documentedModerate: 2,
        predicted: 1,
        safe: 0,
      },
      narrative:
        "Highlights the GraphSAGE fallback predictor calculating link likelihood for pairs lacking direct knowledge base documentation.",
    },
    {
      id: "complex",
      title: "Scenario 4: 5-Drug Complex Polypharmacy",
      category: "Geriatric Polypharmacy",
      drugs: ["Combiflam", "Ecosprin", "Pantop 40", "Metformin 500", "Atorva 10"],
      clinicalFocus:
        "Evaluates all 10 pairwise combinations simultaneously in a single batched Cypher UNWIND execution against Neo4j AuraDB.",
      expectedFindings: {
        documentedMajor: 2,
        documentedModerate: 3,
        predicted: 2,
        safe: 3,
      },
      narrative:
        "Full combinatorial stress test demonstrating sub-second response times and complete evidentiary breakdown.",
    },
  ];

  const [selectedScenario, setSelectedScenario] = useState<DemoScenario>(scenarios[0]);

  return (
    <div className="w-full pb-16 text-left">
      {/* Header Banner */}
      <div className="bg-indigo-900 text-white py-8 border-b border-indigo-950">
        <PageContainer>
          <Breadcrumbs
            items={[{ label: "Defense Demo Mode" }]}
            className="text-indigo-200 mb-2"
          />
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-indigo-700 flex items-center justify-center text-white">
                  <Presentation className="w-5 h-5" />
                </div>
                <h1 className="text-xl sm:text-2xl font-bold tracking-tight">
                  Academic Defense & Evaluation Presentation Mode
                </h1>
              </div>
              <p className="text-xs sm:text-sm text-indigo-200 mt-1">
                Deterministic, click-through demonstration suite designed for thesis defense presentations.
              </p>
            </div>
            <Link href="/analyze">
              <Button
                variant="outline"
                size="sm"
                className="bg-white text-indigo-900 hover:bg-indigo-50 border-transparent font-semibold"
              >
                Switch to Live Workbench
              </Button>
            </Link>
          </div>
        </PageContainer>
      </div>

      <PageContainer className="pt-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Scenario Selector (4 Cols) */}
          <div className="lg:col-span-4 space-y-3">
            <h2 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Select Defense Scenario
            </h2>
            {scenarios.map((sc) => {
              const isSelected = selectedScenario.id === sc.id;
              return (
                <button
                  key={sc.id}
                  onClick={() => setSelectedScenario(sc)}
                  className={`w-full p-4 rounded-lg border text-left transition-all select-none cursor-pointer ${
                    isSelected
                      ? "bg-indigo-50/80 border-indigo-400 shadow-xs"
                      : "bg-white border-slate-200 hover:border-slate-300"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-semibold text-indigo-700">{sc.category}</span>
                    {isSelected && (
                      <span className="w-2 h-2 rounded-full bg-indigo-600 animate-pulse" />
                    )}
                  </div>
                  <h3 className="text-sm font-bold text-slate-900 mb-2">{sc.title}</h3>
                  <div className="flex flex-wrap gap-1">
                    {sc.drugs.map((d, i) => (
                      <span
                        key={i}
                        className="text-[11px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-mono"
                      >
                        {d}
                      </span>
                    ))}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Right Column: Scenario Inspector (8 Cols) */}
          <div className="lg:col-span-8 space-y-6">
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-4">
                <div>
                  <span className="text-xs font-bold text-indigo-700 uppercase tracking-wider">
                    {selectedScenario.category}
                  </span>
                  <h3 className="text-xl font-bold text-slate-900">{selectedScenario.title}</h3>
                </div>
                <Badge variant="sky" size="md">
                  {selectedScenario.drugs.length} Medications
                </Badge>
              </div>

              {/* Medication Chips */}
              <div className="mb-6">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-2">
                  Medication Regimen:
                </span>
                <div className="flex flex-wrap gap-2">
                  {selectedScenario.drugs.map((d, i) => (
                    <div
                      key={i}
                      className="px-3 py-1.5 bg-slate-100 border border-slate-200 rounded-md text-sm font-semibold text-slate-800 flex items-center gap-1.5"
                    >
                      <span>💊</span>
                      <span>{d}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Clinical Focus */}
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 mb-6">
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                  <Info className="w-4 h-4 text-sky-600" />
                  <span>Clinical Defense Teaching Point</span>
                </h4>
                <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
                  {selectedScenario.clinicalFocus}
                </p>
              </div>

              {/* Expected Findings Summary */}
              <div>
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
                  Evidentiary Breakdown Expected:
                </h4>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                  <div className="p-3 bg-red-50 rounded-md border border-red-200">
                    <div className="text-xl font-bold text-red-700">
                      {selectedScenario.expectedFindings.documentedMajor}
                    </div>
                    <div className="text-[11px] font-semibold text-red-900 uppercase mt-0.5">
                      Major Risk
                    </div>
                  </div>

                  <div className="p-3 bg-amber-50 rounded-md border border-amber-200">
                    <div className="text-xl font-bold text-amber-700">
                      {selectedScenario.expectedFindings.documentedModerate}
                    </div>
                    <div className="text-[11px] font-semibold text-amber-900 uppercase mt-0.5">
                      Moderate Risk
                    </div>
                  </div>

                  <div className="p-3 bg-purple-50 rounded-md border border-purple-200">
                    <div className="text-xl font-bold text-purple-700">
                      {selectedScenario.expectedFindings.predicted}
                    </div>
                    <div className="text-[11px] font-semibold text-purple-900 uppercase mt-0.5">
                      AI Predicted
                    </div>
                  </div>

                  <div className="p-3 bg-slate-100 rounded-md border border-slate-200">
                    <div className="text-xl font-bold text-slate-700">
                      {selectedScenario.expectedFindings.safe}
                    </div>
                    <div className="text-[11px] font-semibold text-slate-600 uppercase mt-0.5">
                      No DDI Found
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </PageContainer>
    </div>
  );
}
