import React from "react";
import { CheckResponse } from "@/types/api";
import { ShieldAlert, AlertTriangle, Sparkles, CheckCircle2, Pill } from "lucide-react";

export interface ResultsSummaryBannerProps {
  result: CheckResponse;
  className?: string;
}

export const ResultsSummaryBanner: React.FC<ResultsSummaryBannerProps> = ({
  result,
  className = "",
}) => {
  const {
    total_drugs,
    pairs_checked,
    interactions_found,
    safe_pairs,
    summary,
    interactions = [],
  } = result;

  const majorCount = interactions.filter((i) => i.severity === "MAJOR").length;
  const modCount = interactions.filter((i) => i.severity === "MODERATE").length;
  const minCount = interactions.filter((i) => i.severity === "MINOR").length;
  const predCount = interactions.filter(
    (i) => i.status === "predicted" || i.source === "gnn_predicted"
  ).length;

  return (
    <div
      className={`bg-white rounded-lg border border-slate-200 shadow-xs p-5 text-left space-y-4 ${className}`}
    >
      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <div className="p-3 bg-slate-50 rounded-md border border-slate-200 text-center">
          <div className="text-xl sm:text-2xl font-bold text-slate-900">{total_drugs}</div>
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mt-0.5">
            Medications
          </div>
        </div>

        <div className="p-3 bg-slate-50 rounded-md border border-slate-200 text-center">
          <div className="text-xl sm:text-2xl font-bold text-slate-900">{pairs_checked}</div>
          <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mt-0.5">
            Pairs Evaluated
          </div>
        </div>

        <div className="p-3 bg-red-50/60 rounded-md border border-red-200 text-center">
          <div className="text-xl sm:text-2xl font-bold text-red-700">{interactions_found}</div>
          <div className="text-[11px] font-semibold text-red-900 uppercase tracking-wider mt-0.5 flex items-center justify-center gap-1">
            <span>Interactions</span>
          </div>
        </div>

        <div className="p-3 bg-purple-50/60 rounded-md border border-purple-200 text-center">
          <div className="text-xl sm:text-2xl font-bold text-purple-800">{predCount}</div>
          <div className="text-[11px] font-semibold text-purple-900 uppercase tracking-wider mt-0.5 flex items-center justify-center gap-1">
            <span>AI Predicted</span>
          </div>
        </div>

        <div className="p-3 bg-slate-100 rounded-md border border-slate-200 text-center col-span-2 sm:col-span-1">
          <div className="text-xl sm:text-2xl font-bold text-slate-700">{safe_pairs}</div>
          <div className="text-[11px] font-semibold text-slate-600 uppercase tracking-wider mt-0.5">
            No DDI Found
          </div>
        </div>
      </div>

      {/* Severity Sub-Breakdown Tags & Narrative */}
      <div className="pt-3 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center flex-wrap gap-2">
          <span className="font-semibold text-slate-600">Breakdown:</span>
          {majorCount > 0 && (
            <span className="px-2 py-0.5 bg-red-100 text-red-800 rounded font-semibold font-mono">
              🔴 {majorCount} Major
            </span>
          )}
          {modCount > 0 && (
            <span className="px-2 py-0.5 bg-amber-100 text-amber-900 rounded font-semibold font-mono">
              🟡 {modCount} Moderate
            </span>
          )}
          {minCount > 0 && (
            <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded font-semibold font-mono">
              🟢 {minCount} Minor
            </span>
          )}
          {predCount > 0 && (
            <span className="px-2 py-0.5 bg-purple-100 text-purple-900 rounded font-semibold font-mono">
              🤖 {predCount} Predicted
            </span>
          )}
        </div>

        <p className="text-slate-600 font-medium sm:text-right max-w-md">{summary}</p>
      </div>
    </div>
  );
};
