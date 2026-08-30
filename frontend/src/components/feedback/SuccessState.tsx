import React from "react";
import { CheckCircle2 } from "lucide-react";

export interface SuccessStateProps {
  title?: string;
  message: string;
  action?: React.ReactNode;
  className?: string;
}

export const SuccessState: React.FC<SuccessStateProps> = ({
  title = "Analysis Complete",
  message,
  action,
  className = "",
}) => {
  return (
    <div
      className={`p-4 bg-emerald-50/70 border border-emerald-200 rounded-lg flex items-start gap-3 text-left ${className}`}
      role="status"
    >
      <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
      <div className="flex-1">
        <h4 className="text-sm font-semibold text-emerald-900">{title}</h4>
        <p className="text-xs text-emerald-700 mt-0.5 leading-relaxed">{message}</p>
        {action && <div className="mt-3">{action}</div>}
      </div>
    </div>
  );
};
