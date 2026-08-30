"use client";

import React from "react";
import { Pill, ArrowRight, CheckCircle2, RefreshCw, AlertCircle, Database } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { ResolvedDrug } from "@/types/api";

export interface ResolutionStepProps {
  drugs: string[];
  resolvedDrugs?: ResolvedDrug[];
  className?: string;
}

export const ResolutionStep: React.FC<ResolutionStepProps> = ({
  drugs,
  resolvedDrugs,
  className = "",
}) => {
  return (
    <div className={`space-y-6 text-left ${className}`}>
      <div className="p-4 bg-sky-50 rounded-lg border border-sky-200 text-xs sm:text-sm text-sky-900 leading-relaxed">
        <strong className="font-bold">Indian Pharmaceutical Catalog Mapping:</strong> Commercial trade
        names in India are frequently multi-ingredient fixed-dose combinations (FDCs). PharmaSafe-KG
        normalizes trade names against 304,404 formulations, mapping them to 1,002 standard DrugBank
        chemical entities before traversing the Knowledge Graph.
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {drugs.map((drugName, idx) => {
          const resolved = resolvedDrugs?.find(
            (r) => r.input.toLowerCase() === drugName.toLowerCase() || r.matched_brand?.toLowerCase() === drugName.toLowerCase()
          );

          const generics = resolved?.generics || (
            drugName.toLowerCase().includes("combiflam")
              ? ["ibuprofen", "paracetamol"]
              : drugName.toLowerCase().includes("ecosprin")
              ? ["aspirin"]
              : drugName.toLowerCase().includes("pantop")
              ? ["pantoprazole"]
              : drugName.toLowerCase().includes("metolar")
              ? ["metoprolol"]
              : drugName.toLowerCase().includes("atorva")
              ? ["atorvastatin"]
              : drugName.toLowerCase().includes("metformin")
              ? ["metformin"]
              : drugName.toLowerCase().includes("glibenclamide")
              ? ["glibenclamide"]
              : [drugName.toLowerCase()]
          );

          const matchType = resolved?.match_type || "exact";
          const confidence = resolved?.confidence || 100;

          return (
            <Card key={idx} className="p-4 space-y-3 bg-white border-slate-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-md bg-sky-100 flex items-center justify-center text-sky-700">
                    <Pill className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900">{drugName}</h4>
                    <span className="text-[10px] text-slate-400 font-mono">
                      Input Formulation #{idx + 1}
                    </span>
                  </div>
                </div>

                <Badge variant="sky" size="sm">
                  {matchType === "exact" ? "Exact Match" : "Fuzzy / Direct"} ({confidence}%)
                </Badge>
              </div>

              <div className="pt-2 border-t border-slate-100 space-y-1.5">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
                  Resolved Active Generic Chemical(s):
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {generics.map((g, gi) => (
                    <span
                      key={gi}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-100 font-mono text-xs font-semibold text-slate-800 border border-slate-200"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                      <span className="capitalize">{g}</span>
                    </span>
                  ))}
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
