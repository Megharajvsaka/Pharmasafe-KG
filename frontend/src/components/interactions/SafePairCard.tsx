import React from "react";
import { Info, Check } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { SafePair } from "@/types/api";

export interface SafePairCardProps {
  pair: SafePair;
  className?: string;
}

export const SafePairCard: React.FC<SafePairCardProps> = ({ pair, className = "" }) => {
  return (
    <Card accent="safe" className={`p-4 text-left bg-slate-50/50 ${className}`}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <Info className="w-4 h-4 text-slate-500 shrink-0" />
          <h4 className="text-sm font-semibold text-slate-800">
            {pair.brand_a} <span className="text-slate-400">+</span> {pair.brand_b}
          </h4>
        </div>
        <Badge variant="safe" size="sm">
          No Documented DDI
        </Badge>
      </div>
      <p className="text-xs text-slate-500 leading-relaxed pl-6">
        {pair.note ||
          "No documented interaction in the current knowledge base. Absence of documented evidence does not guarantee clinical safety."}
      </p>
    </Card>
  );
};
