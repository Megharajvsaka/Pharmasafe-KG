"use client";

import React from "react";
import { GitGraph, Database, CheckCircle2, ShieldCheck, Layers, Award } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

export const MetricsStep: React.FC<{ className?: string }> = ({ className = "" }) => {
  return (
    <div className={`space-y-6 text-left ${className}`}>
      <div className="p-4 bg-sky-50 rounded-lg border border-sky-200 text-xs sm:text-sm text-sky-950 leading-relaxed">
        <strong className="font-bold">Empirical Research Validation:</strong> The following benchmarks were
        forensically validated on a held-out test split of 21,325 pairs (13,825 positive, 7,500 negative)
        with zero test edge leakage into message passing.
      </div>

      {/* Top 4 Stat Tiles */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-4 bg-white rounded-lg border border-slate-200 shadow-2xs text-center">
          <div className="text-2xl sm:text-3xl font-bold text-sky-700 font-mono">50,073</div>
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mt-1">
            Knowledge Graph Nodes
          </div>
          <span className="text-[10px] text-slate-400">2,073 generic + 48,000 brand</span>
        </div>

        <div className="p-4 bg-white rounded-lg border border-slate-200 shadow-2xs text-center">
          <div className="text-2xl sm:text-3xl font-bold text-emerald-700 font-mono">89,367</div>
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mt-1">
            DDI Relationships
          </div>
          <span className="text-[10px] text-slate-400">72.7% Mod, 22.9% Maj, 4.3% Min</span>
        </div>

        <div className="p-4 bg-white rounded-lg border border-slate-200 shadow-2xs text-center">
          <div className="text-2xl sm:text-3xl font-bold text-purple-700 font-mono">0.8834</div>
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mt-1">
            GraphSAGE Test ROC-AUC
          </div>
          <span className="text-[10px] text-purple-600 font-medium">N = 21,325 Held-out pairs</span>
        </div>

        <div className="p-4 bg-white rounded-lg border border-slate-200 shadow-2xs text-center">
          <div className="text-2xl sm:text-3xl font-bold text-indigo-700 font-mono">0.8330</div>
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mt-1">
            GraphSAGE Test F1
          </div>
          <span className="text-[10px] text-slate-400">Precision: 0.72 | Recall: 0.98</span>
        </div>
      </div>

      {/* Model Benchmark Comparison Table */}
      <Card className="p-5 bg-white border-slate-200">
        <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <Award className="w-5 h-5 text-purple-600" />
            <h3 className="text-sm font-bold text-slate-900">
              Table 2: GNN Inductive Link Prediction Benchmarks (Leakage-Free Test Split)
            </h3>
          </div>
          <Badge variant="predicted" size="sm">
            Held-Out Test Split
          </Badge>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-semibold uppercase text-[10px] tracking-wider">
                <th className="py-2.5 px-3">Architecture</th>
                <th className="py-2.5 px-3">Layers & Channels</th>
                <th className="py-2.5 px-3">ROC-AUC</th>
                <th className="py-2.5 px-3">F1-Score</th>
                <th className="py-2.5 px-3">Recall</th>
                <th className="py-2.5 px-3">Precision</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700 font-mono text-xs">
              <tr className="bg-purple-50/40 font-semibold text-purple-950">
                <td className="py-3 px-3 font-sans">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-purple-600" />
                    <span>GraphSAGE (PharmaSafe-KG)</span>
                  </div>
                </td>
                <td className="py-3 px-3 font-mono">3 Layers (128→64→32)</td>
                <td className="py-3 px-3 font-bold text-purple-800">0.8834</td>
                <td className="py-3 px-3 font-bold text-purple-800">0.8330</td>
                <td className="py-3 px-3">0.9851</td>
                <td className="py-3 px-3">0.7215</td>
                <td className="py-3 px-3">
                  <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded text-[10px] font-sans font-bold uppercase">
                    Deployed Model
                  </span>
                </td>
              </tr>
              <tr className="text-slate-600">
                <td className="py-3 px-3 font-sans">GAT Baseline (Veličković et al.)</td>
                <td className="py-3 px-3 font-mono">2 Layers (4-Head Attn)</td>
                <td className="py-3 px-3">0.8520</td>
                <td className="py-3 px-3">0.8010</td>
                <td className="py-3 px-3">0.9240</td>
                <td className="py-3 px-3">0.7080</td>
                <td className="py-3 px-3">
                  <span className="px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-[10px] font-sans">
                    Comparison Baseline
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
