"use client";

import React from "react";
import { Check } from "lucide-react";

export interface DemoStepItem {
  id: string;
  number: number;
  title: string;
  shortLabel: string;
  category: "overview" | "pipeline" | "evidence" | "gnn" | "validation";
}

export interface DemoProgressProps {
  steps: DemoStepItem[];
  currentStepIndex: number;
  onStepSelect: (index: number) => void;
  className?: string;
}

export const DemoProgress: React.FC<DemoProgressProps> = ({
  steps,
  currentStepIndex,
  onStepSelect,
  className = "",
}) => {
  const progressPercent = ((currentStepIndex + 1) / steps.length) * 100;
  const currentStep = steps[currentStepIndex];

  return (
    <div className={`w-full bg-white border-b border-slate-200 py-3.5 px-4 sm:px-8 ${className}`}>
      <div className="max-w-6xl mx-auto space-y-2.5">
        {/* Step Counter & Category */}
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <span className="font-mono font-bold text-sky-700 bg-sky-50 px-2 py-0.5 rounded border border-sky-200">
              STEP {currentStepIndex + 1} OF {steps.length}
            </span>
            <span className="font-semibold text-slate-800 hidden sm:inline-block">
              {currentStep.title}
            </span>
          </div>

          <span className="text-[11px] font-semibold text-slate-400 font-mono">
            {Math.round(progressPercent)}% COMPLETED
          </span>
        </div>

        {/* Continuous Progress Bar */}
        <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
          <div
            className="bg-sky-600 h-full rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        {/* Step Buttons (Desktop) */}
        <div className="hidden lg:flex items-center justify-between pt-1">
          {steps.map((step, idx) => {
            const isCompleted = idx < currentStepIndex;
            const isCurrent = idx === currentStepIndex;

            return (
              <button
                key={step.id}
                onClick={() => onStepSelect(idx)}
                className={`flex items-center gap-1.5 text-[11px] font-medium py-1 px-2 rounded transition-colors cursor-pointer select-none ${
                  isCurrent
                    ? "bg-sky-50 text-sky-900 font-bold border border-sky-200"
                    : isCompleted
                    ? "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                    : "text-slate-400 hover:text-slate-600"
                }`}
                title={`Jump to Step ${idx + 1}: ${step.title}`}
              >
                <span
                  className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold ${
                    isCurrent
                      ? "bg-sky-600 text-white"
                      : isCompleted
                      ? "bg-emerald-100 text-emerald-800"
                      : "bg-slate-200 text-slate-600"
                  }`}
                >
                  {isCompleted ? <Check className="w-2.5 h-2.5" /> : idx + 1}
                </span>
                <span className="truncate max-w-[100px]">{step.shortLabel}</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
