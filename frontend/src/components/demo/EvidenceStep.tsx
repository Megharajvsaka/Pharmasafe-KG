"use client";

import React from "react";
import { Database, ShieldAlert, AlertTriangle, Info, BookOpen, CheckCircle2 } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { InteractionResult } from "@/types/api";

export interface EvidenceStepProps {
  interactions: InteractionResult[];
  className?: string;
}

export const EvidenceStep: React.FC<EvidenceStepProps> = ({
  interactions,
  className = "",
}) => {
  const documentedHits = interactions.filter(
    (i) => i.status === "documented" || i.source === "knowledge_graph"
  );

  return (
    <div className={`space-y-6 text-left ${className}`}>
      <div className="p-4 bg-emerald-50 rounded-lg border border-emerald-200 text-xs sm:text-sm text-emerald-950 leading-relaxed">
        <strong className="font-bold">Knowledge Graph Traversal:</strong> A single batched Cypher UNWIND
        query matches all resolved active ingredients against the 89,367 validated INTERACTS_WITH
        relationships in Neo4j AuraDB. Interactions are graded into MAJOR, MODERATE, and MINOR severity with
        full mechanism monographs.
      </div>

      {documentedHits.length === 0 ? (
        <Card className="p-8 text-center bg-slate-50 border-slate-200">
          <Info className="w-8 h-8 text-slate-400 mx-auto mb-2" />
          <h4 className="text-sm font-bold text-slate-800">No Documented Interaction Found in Knowledge Base</h4>
          <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
            These active chemical entities do not share an existing INTERACTS_WITH edge in DrugBank.
            The system automatically triggers the inductive GraphSAGE GNN fallback in the next step.
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          {documentedHits.map((hit, idx) => {
            const isMajor = hit.severity === "MAJOR";
            const isModerate = hit.severity === "MODERATE";

            return (
              <Card
                key={idx}
                accent={isMajor ? "major" : isModerate ? "moderate" : "minor"}
                className="p-5 space-y-3 bg-white"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    {isMajor ? (
                      <ShieldAlert className="w-5 h-5 text-red-600 shrink-0" />
                    ) : (
                      <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />
                    )}
                    <div>
                      <h4 className="text-sm sm:text-base font-bold text-slate-900">
                        {hit.brand_a} ↔ {hit.brand_b}
                      </h4>
                      <span className="text-xs text-slate-500 font-mono">
                        Active Generics: {hit.ingredient_a} ↔ {hit.ingredient_b}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5 flex-wrap">
                    <Badge severity={hit.severity} size="sm">
                      {hit.severity} Risk
                    </Badge>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-50 text-emerald-800 border border-emerald-300">
                      <Database className="w-3 h-3 text-emerald-600" />
                      <span>Documented Evidence</span>
                    </span>
                  </div>
                </div>

                <div className="p-3 bg-slate-50 rounded border border-slate-200/80 text-xs sm:text-sm text-slate-700 leading-relaxed">
                  <strong className="text-slate-900 block mb-1">Clinical Explanation:</strong>
                  {hit.explanation || hit.mechanism}
                </div>

                <div className="text-[11px] text-slate-400 flex items-center justify-between pt-1 border-t border-slate-100">
                  <span className="flex items-center gap-1">
                    <BookOpen className="w-3.5 h-3.5 text-slate-400" />
                    <span>Evidence Source: DrugBank Biomedical Monograph</span>
                  </span>
                  <span className="font-mono text-slate-500">Neo4j Cypher Traversal Verified</span>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};
