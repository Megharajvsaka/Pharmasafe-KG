"use client";

import React from "react";
import Link from "next/link";
import {
  CheckCircle2,
  ShieldCheck,
  FlaskConical,
  GitGraph,
  BookOpen,
  Award,
  ArrowRight,
  AlertTriangle,
} from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export const ConclusionStep: React.FC<{ className?: string }> = ({ className = "" }) => {
  const contributions = [
    {
      title: "Commercial Indian Brand-to-Generic Resolution",
      desc: "Handles multi-ingredient FDC formulations across 304,404 Indian medicine entries mapped to 1,002 DrugBank chemical entities.",
    },
    {
      title: "Scalable Knowledge Graph Traversal",
      desc: "50,073 nodes and 89,367 relationships evaluated via single batched Cypher UNWIND query execution in sub-second latency.",
    },
    {
      title: "Inductive GraphSAGE Link Prediction",
      desc: "Leakage-free GNN architecture achieving 0.8834 ROC-AUC on held-out test split, overcoming database incompleteness.",
    },
    {
      title: "Strict Epistemic Transparency",
      desc: "Clear visual separation between peer-reviewed clinical monographs and statistical AI link predictions.",
    },
    {
      title: "Polypharmacy Combinatorial Analysis",
      desc: "Simultaneous evaluation of 2–10 medications across all combinatorial pairs with structured XAI explanations.",
    },
    {
      title: "Zero-Hallucination Explainability",
      desc: "Mechanistic monographs and structural graph evidence delivered with full source lineage and no synthetic facts.",
    },
  ];

  return (
    <div className={`space-y-6 text-left ${className}`}>
      {/* Top Banner */}
      <div className="p-5 bg-emerald-50 rounded-lg border border-emerald-200 flex items-start gap-3">
        <div className="w-10 h-10 rounded-lg bg-emerald-600 flex items-center justify-center text-white shrink-0 mt-0.5 shadow-2xs">
          <Award className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-base font-bold text-emerald-950">
            Thesis Defense Summary: PharmaSafe-KG
          </h3>
          <p className="text-xs sm:text-sm text-emerald-900 mt-1 leading-relaxed">
            PharmaSafe-KG demonstrates a comprehensive, explainable neuro-symbolic framework for drug safety,
            combining deterministic graph querying with inductive deep learning for commercial polypharmacy.
          </p>
        </div>
      </div>

      {/* 6 Key Contributions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
        {contributions.map((item, idx) => (
          <Card key={idx} className="p-4 space-y-1.5 bg-white border-slate-200">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <h4 className="text-xs sm:text-sm font-bold text-slate-900">{item.title}</h4>
            </div>
            <p className="text-xs text-slate-600 pl-6 leading-relaxed">{item.desc}</p>
          </Card>
        ))}
      </div>

      {/* Clinical Governance Notice */}
      <div className="p-4 bg-slate-100/80 rounded-lg border border-slate-200 text-xs text-slate-700 leading-relaxed flex items-start gap-2.5">
        <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <strong className="text-slate-900">Clinical Decision-Support Disclaimer:</strong> PharmaSafe-KG
          is an engineering research prototype designed to assist clinical research and pharmacology studies.
          It does not substitute for licensed healthcare professional consultation or specialized clinical judgment.
        </div>
      </div>

      {/* Next Actions */}
      <div className="flex flex-col sm:flex-row items-center justify-end gap-3 pt-2">
        <Link href="/graph">
          <Button variant="outline" leftIcon={<GitGraph className="w-4 h-4" />}>
            Explore Full Knowledge Graph
          </Button>
        </Link>
        <Link href="/analyze">
          <Button variant="primary" rightIcon={<ArrowRight className="w-4 h-4" />}>
            Open Live Medication Workbench
          </Button>
        </Link>
      </div>
    </div>
  );
};
