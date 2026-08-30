"use client";

import React from "react";
import {
  ShieldAlert,
  AlertTriangle,
  Info,
  Sparkles,
  Database,
  ArrowRightLeft,
  Pill,
} from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { EvidenceAccordion } from "@/components/interactions/EvidenceAccordion";
import { InteractionResult } from "@/types/api";

export interface InteractionCardProps {
  interaction: InteractionResult;
  className?: string;
}

export const InteractionCard: React.FC<InteractionCardProps> = ({
  interaction,
  className = "",
}) => {
  const {
    brand_a,
    brand_b,
    ingredient_a,
    ingredient_b,
    severity,
    mechanism,
    explanation,
    status,
    source,
    confidence,
    evidence,
  } = interaction;

  const isPredicted = status === "predicted" || source === "gnn_predicted";

  const getSeverityIcon = () => {
    switch (severity) {
      case "MAJOR":
        return <ShieldAlert className="w-4 h-4 text-red-600 shrink-0" />;
      case "MODERATE":
        return <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />;
      case "MINOR":
        return <Info className="w-4 h-4 text-emerald-600 shrink-0" />;
      case "UNKNOWN":
      case "UNASSESSED":
      default:
        return <Sparkles className="w-4 h-4 text-purple-600 shrink-0" />;
    }
  };

  const getCardAccent = () => {
    if (isPredicted) return "predicted";
    switch (severity) {
      case "MAJOR":
        return "major";
      case "MODERATE":
        return "moderate";
      case "MINOR":
        return "minor";
      default:
        return "none";
    }
  };

  return (
    <Card accent={getCardAccent()} className={`p-4 sm:p-5 text-left ${className}`}>
      {/* Header: Brands + Badges */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 mb-3">
        <div className="flex items-center gap-2">
          {getSeverityIcon()}
          <h3 className="text-sm sm:text-base font-bold text-slate-900 flex items-center gap-2">
            <span>{brand_a}</span>
            <ArrowRightLeft className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span>{brand_b}</span>
          </h3>
        </div>

        <div className="flex items-center flex-wrap gap-1.5">
          {/* Severity Badge */}
          {isPredicted ? (
            <Badge variant="predicted" size="sm">
              Severity: Unassessed
            </Badge>
          ) : (
            <Badge severity={severity} size="sm">
              {severity} Risk
            </Badge>
          )}

          {/* Evidence Source Badge */}
          {isPredicted ? (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-purple-100 text-purple-900 border border-purple-300">
              <Sparkles className="w-3 h-3 text-purple-700" />
              <span>
                AI Predicted {confidence ? `(${Math.round(confidence * 100)}% Conf)` : ""}
              </span>
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-50 text-emerald-800 border border-emerald-300">
              <Database className="w-3 h-3 text-emerald-600" />
              <span>Documented Evidence</span>
            </span>
          )}
        </div>
      </div>

      {/* Active Chemical Entities Tag */}
      <div className="flex items-center gap-1.5 text-xs text-slate-500 mb-3 flex-wrap">
        <span className="font-semibold text-slate-600">Active Generics:</span>
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-100 font-mono text-[11px] text-slate-800 border border-slate-200">
          <Pill className="w-3 h-3 text-slate-500" />
          {ingredient_a}
        </span>
        <span className="text-slate-400">↔</span>
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-100 font-mono text-[11px] text-slate-800 border border-slate-200">
          <Pill className="w-3 h-3 text-slate-500" />
          {ingredient_b}
        </span>
      </div>

      {/* Mechanism & Explanation */}
      <div className="space-y-2 text-xs sm:text-sm">
        {explanation && (
          <p className="text-slate-800 font-medium leading-relaxed bg-slate-50/70 p-3 rounded border border-slate-100">
            {explanation}
          </p>
        )}

        {mechanism && mechanism !== explanation && (
          <div className="text-xs text-slate-600 leading-relaxed font-sans pl-1">
            <span className="font-semibold text-slate-700 block text-[11px] uppercase tracking-wider mb-0.5">
              Pharmacological Mechanism:
            </span>
            {mechanism}
          </div>
        )}

        {/* AI Disclaimer Notice */}
        {isPredicted && (
          <div className="p-2.5 bg-purple-50/60 rounded border border-purple-200/80 text-[11px] text-purple-900 leading-relaxed">
            <strong>Statistical AI Link Prediction:</strong> This interaction link was predicted by
            inductive GraphSAGE neighbor aggregation. It indicates high topological similarity but
            has not yet been validated by peer-reviewed clinical monograph sources.
          </div>
        )}
      </div>

      {/* Expandable Evidentiary Records */}
      <EvidenceAccordion evidence={evidence} source={source} />
    </Card>
  );
};
