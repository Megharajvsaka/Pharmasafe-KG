"use client";

import React, { useState } from "react";
import { ChevronDown, Database, Sparkles, BookOpen } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { EvidenceItem } from "@/types/api";

export interface EvidenceAccordionProps {
  evidence: EvidenceItem[];
  source: "knowledge_graph" | "gnn_predicted";
  className?: string;
}

export const EvidenceAccordion: React.FC<EvidenceAccordionProps> = ({
  evidence,
  source,
  className = "",
}) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!evidence || evidence.length === 0) {
    return null;
  }

  const isPredicted = source === "gnn_predicted";

  return (
    <div className={`mt-3 pt-3 border-t border-slate-100 ${className}`}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        className="flex items-center justify-between w-full text-xs font-semibold text-slate-600 hover:text-slate-900 transition-colors py-1 select-none cursor-pointer focus-visible:outline-sky-600 rounded"
      >
        <span className="flex items-center gap-1.5">
          {isPredicted ? (
            <Sparkles className="w-3.5 h-3.5 text-purple-600" />
          ) : (
            <Database className="w-3.5 h-3.5 text-emerald-600" />
          )}
          <span>
            {isPredicted ? "Model Link Prediction Parameters" : `Evidentiary Records (${evidence.length})`}
          </span>
        </span>
        <ChevronDown
          className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 ${
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
            <div className="pt-2 space-y-2 text-xs">
              {evidence.map((item, idx) => (
                <div
                  key={idx}
                  className="p-2.5 bg-slate-50 rounded border border-slate-200/80 text-left space-y-1"
                >
                  {isPredicted ? (
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 font-mono text-[11px] text-slate-700">
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-sans">Model</span>
                        <span className="font-semibold text-purple-900">{item.model || "GraphSAGE"}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-sans">Probability</span>
                        <span className="font-semibold text-purple-900">
                          {typeof item.probability === "number" ? `${(item.probability * 100).toFixed(1)}%` : "N/A"}
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-sans">Threshold</span>
                        <span className="font-semibold text-slate-700">
                          {typeof item.threshold === "number" ? item.threshold.toFixed(2) : "0.70"}
                        </span>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="flex items-center justify-between text-[11px] text-slate-500 font-medium">
                        <span className="flex items-center gap-1">
                          <BookOpen className="w-3 h-3 text-slate-400" />
                          <span>Source: {item.source || "DrugBank Knowledge Graph"}</span>
                        </span>
                        {item.severity && (
                          <span className="font-semibold text-slate-700 font-mono text-[10px]">
                            {item.severity}
                          </span>
                        )}
                      </div>
                      {item.mechanism && (
                        <p className="text-slate-600 text-[11px] leading-relaxed pt-0.5">
                          {item.mechanism}
                        </p>
                      )}
                    </>
                  )}
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
