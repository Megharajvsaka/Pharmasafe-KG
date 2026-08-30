"use client";

import React, { useState } from "react";
import {
  Layers,
  Database,
  GitGraph,
  Cpu,
  FileCheck,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

export const ArchitectureDiagram: React.FC<{ className?: string }> = ({ className = "" }) => {
  const [activeStage, setActiveStage] = useState<number>(0);

  const stages = [
    {
      id: "ingestion",
      step: "01",
      title: "Indian Formulation Ingestion",
      icon: <Database className="w-5 h-5 text-sky-600" />,
      tag: "Data Provenance",
      description:
        "Ingests 304,404 commercial formulations from the Tata 1mg catalog and 92,161 DDI records from DrugBank. Cleanses fixed-dose combinations and maps trade names to 1,002 standardized active generic chemical entities.",
      badge: "304k Formulations",
    },
    {
      id: "graph",
      step: "02",
      title: "Neo4j AuraDB Knowledge Graph",
      icon: <GitGraph className="w-5 h-5 text-emerald-600" />,
      tag: "Knowledge Base",
      description:
        "Stores 50,073 nodes (2,073 generic Ingredients + 48,000 brand Drugs) and 89,367 validated INTERACTS_WITH relationships categorized by severity (72.75% MODERATE, 22.91% MAJOR, 4.34% MINOR).",
      badge: "50,073 Nodes",
    },
    {
      id: "engine",
      step: "03",
      title: "FastAPI Polypharmacy Engine",
      icon: <Cpu className="w-5 h-5 text-indigo-600" />,
      tag: "Query Engine",
      description:
        "Executes a single batched Cypher UNWIND query to evaluate all pairwise combinations simultaneously. Resolves brand formulations and extracts clinical mechanism monographs in sub-second latency.",
      badge: "Batched UNWIND",
    },
    {
      id: "gnn",
      step: "04",
      title: "Inductive GraphSAGE Link Predictor",
      icon: <Layers className="w-5 h-5 text-purple-600" />,
      tag: "Machine Learning",
      description:
        "Evaluates pairs lacking direct KG records using a 3-layer GraphSAGE GNN (128 → 64 → 32). Aggregates 10-dimensional node feature neighborhoods to predict topological interaction probability (threshold ≥ 0.70).",
      badge: "AUC 0.8834",
    },
    {
      id: "output",
      step: "05",
      title: "Explainable Clinical Output Layer",
      icon: <FileCheck className="w-5 h-5 text-amber-600" />,
      tag: "Clinical XAI",
      description:
        "Delivers transparent severity-ranked findings with strict epistemic separation: DOCUMENTED EVIDENCE is grounded in indexed literature, while AI PREDICTIONS are explicitly flagged as experimental statistical inferences.",
      badge: "Transparent XAI",
    },
  ];

  return (
    <div className={`space-y-6 text-left ${className}`}>
      {/* 5-Step Pipeline Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-5 gap-2">
        {stages.map((stage, idx) => {
          const isActive = idx === activeStage;
          return (
            <button
              key={stage.id}
              onClick={() => setActiveStage(idx)}
              className={`p-3.5 rounded-lg border text-left transition-all select-none cursor-pointer ${
                isActive
                  ? "bg-sky-50 border-sky-400 shadow-xs ring-1 ring-sky-400"
                  : "bg-white border-slate-200 hover:border-slate-300"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-mono font-bold text-slate-400">
                  {stage.step}
                </span>
                {stage.icon}
              </div>
              <h4 className="text-xs font-bold text-slate-900 line-clamp-1 mb-1">
                {stage.title}
              </h4>
              <span className="text-[10px] font-semibold text-sky-700 bg-white px-1.5 py-0.5 rounded border border-slate-200 inline-block">
                {stage.badge}
              </span>
            </button>
          );
        })}
      </div>

      {/* Selected Stage Detail Card */}
      <Card className="p-6 bg-slate-50 border-slate-200">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200/80 pb-3 mb-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-white border border-slate-200 shadow-2xs">
              {stages[activeStage].icon}
            </div>
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-sky-700">
                {stages[activeStage].tag}
              </span>
              <h3 className="text-base font-bold text-slate-900">
                {stages[activeStage].title}
              </h3>
            </div>
          </div>
          <Badge variant="sky" size="sm">
            Stage {stages[activeStage].step} Architecture
          </Badge>
        </div>

        <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
          {stages[activeStage].description}
        </p>

        <div className="mt-4 pt-3 border-t border-slate-200/60 flex items-center justify-between text-xs text-slate-500">
          <span>Click any stage above to inspect its scientific role</span>
          <span className="font-semibold text-slate-700">
            Stage {activeStage + 1} of 5
          </span>
        </div>
      </Card>
    </div>
  );
};
