"use client";

import React, { useState } from "react";
import Link from "next/link";
import { ChevronDown, CheckCircle2, RefreshCw, AlertCircle, Pill, ExternalLink } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { ResolvedDrug } from "@/types/api";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

export interface ResolvedDrugsTableProps {
  resolvedDrugs: ResolvedDrug[];
  className?: string;
}

export const ResolvedDrugsTable: React.FC<ResolvedDrugsTableProps> = ({
  resolvedDrugs,
  className = "",
}) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!resolvedDrugs || resolvedDrugs.length === 0) return null;

  const getMatchBadge = (type: string, confidence: number) => {
    switch (type) {
      case "exact":
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
            <CheckCircle2 className="w-3 h-3 text-emerald-600" />
            Exact Match
          </span>
        );
      case "alias":
      case "generic_direct":
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-sky-800 bg-sky-50 px-2 py-0.5 rounded border border-sky-200">
            <CheckCircle2 className="w-3 h-3 text-sky-600" />
            Generic / Alias
          </span>
        );
      case "fuzzy":
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
            <RefreshCw className="w-3 h-3 text-amber-600" />
            Fuzzy Match ({confidence}%)
          </span>
        );
      case "not_found":
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-red-800 bg-red-50 px-2 py-0.5 rounded border border-red-200">
            <AlertCircle className="w-3 h-3 text-red-600" />
            Unresolved
          </span>
        );
    }
  };

  return (
    <Card className={`p-4 text-left ${className}`}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        className="flex items-center justify-between w-full text-xs sm:text-sm font-bold text-slate-900 transition-colors select-none cursor-pointer focus-visible:outline-sky-600 rounded"
      >
        <span className="flex items-center gap-2">
          <Pill className="w-4 h-4 text-sky-600" />
          <span>Brand-to-Generic Resolution Lineage ({resolvedDrugs.length} Drugs)</span>
        </span>
        <ChevronDown
          className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${
            isOpen ? "rotate-180 text-slate-700" : ""
          }`}
        />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="pt-4 overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-semibold uppercase text-[10px] tracking-wider">
                    <th className="py-2.5 px-3">Input Name</th>
                    <th className="py-2.5 px-3">Matched Brand</th>
                    <th className="py-2.5 px-3">Active Chemical Ingredients</th>
                    <th className="py-2.5 px-3">Resolution Type</th>
                    <th className="py-2.5 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {resolvedDrugs.map((rd, idx) => {
                    const brandTarget = rd.matched_brand || rd.input;
                    const canViewMonograph = rd.match_type !== "not_found";

                    return (
                      <tr key={idx} className="hover:bg-slate-50/70 transition-colors">
                        <td className="py-2.5 px-3 font-semibold text-slate-900">{rd.input}</td>
                        <td className="py-2.5 px-3 text-slate-600">{rd.matched_brand || "—"}</td>
                        <td className="py-2.5 px-3">
                          {rd.generics && rd.generics.length > 0 ? (
                            <div className="flex flex-wrap gap-1">
                              {rd.generics.map((g, gi) => (
                                <span
                                  key={gi}
                                  className="px-1.5 py-0.5 bg-slate-100 border border-slate-200 rounded font-mono text-[11px] text-slate-800"
                                >
                                  {g}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <span className="text-red-500 italic text-[11px]">None resolved</span>
                          )}
                        </td>
                        <td className="py-2.5 px-3">{getMatchBadge(rd.match_type, rd.confidence)}</td>
                        <td className="py-2.5 px-3 text-right">
                          {canViewMonograph ? (
                            <Link
                              href={`/drugs/${encodeURIComponent(brandTarget)}`}
                              className="inline-flex items-center gap-1 text-[11px] font-semibold text-sky-600 hover:text-sky-800 hover:underline"
                            >
                              <span>Monograph</span>
                              <ExternalLink className="w-3 h-3" />
                            </Link>
                          ) : (
                            <span className="text-slate-400 text-[11px]">—</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
};
