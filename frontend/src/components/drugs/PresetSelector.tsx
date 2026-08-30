"use client";

import React from "react";
import { Sparkles, Layers } from "lucide-react";

export interface PresetItem {
  id: string;
  label: string;
  description: string;
  drugs: string[];
}

export interface PresetSelectorProps {
  onSelectPreset: (drugs: string[]) => void;
  className?: string;
}

export const defaultPresets: PresetItem[] = [
  {
    id: "warfarin",
    label: "Warfarin Bleed Risk",
    description: "Warfarin + Combiflam + Pantop 40 (Major gastrointestinal risk)",
    drugs: ["Warfarin", "Combiflam", "Pantop 40"],
  },
  {
    id: "cardiac",
    label: "Cardiovascular Regimen",
    description: "Atorva 10 + Ecosprin + Metolar XR (Triple cardio therapy)",
    drugs: ["Atorva 10", "Ecosprin", "Metolar XR"],
  },
  {
    id: "diabetes",
    label: "Diabetes Combination",
    description: "Metformin 500 + Glibenclamide + Ecosprin (Dual glycaemic therapy)",
    drugs: ["Metformin 500", "Glibenclamide", "Ecosprin"],
  },
  {
    id: "polypharmacy",
    label: "5-Drug Complex Regimen",
    description: "Combiflam + Ecosprin + Pantop 40 + Metformin 500 + Atorva 10 (10 pairs)",
    drugs: ["Combiflam", "Ecosprin", "Pantop 40", "Metformin 500", "Atorva 10"],
  },
];

export const PresetSelector: React.FC<PresetSelectorProps> = ({
  onSelectPreset,
  className = "",
}) => {
  return (
    <div className={className}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-sky-600" />
          <span>Quick Clinical Test Regimens</span>
        </span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {defaultPresets.map((preset) => (
          <button
            key={preset.id}
            type="button"
            onClick={() => onSelectPreset(preset.drugs)}
            className="p-2.5 text-left bg-slate-50 hover:bg-sky-50/80 hover:border-sky-300 border border-slate-200 rounded-md transition-all text-slate-800 font-medium select-none cursor-pointer focus-visible:outline-sky-600"
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-bold text-slate-900">{preset.label}</span>
              <span className="text-[10px] font-semibold bg-white text-slate-600 px-1.5 py-0.5 rounded border border-slate-200">
                {preset.drugs.length} drugs
              </span>
            </div>
            <p className="text-[11px] text-slate-500 line-clamp-1">{preset.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
};
