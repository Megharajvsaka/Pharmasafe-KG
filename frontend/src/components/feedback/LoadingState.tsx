import React from "react";
import { Loader2 } from "lucide-react";

export interface LoadingStateProps {
  message?: string;
  description?: string;
  className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = "Processing clinical query...",
  description = "Searching the Knowledge Graph and evaluating topological link predictions.",
  className = "",
}) => {
  return (
    <div
      className={`flex flex-col items-center justify-center p-8 text-center bg-white rounded-lg border border-slate-200 ${className}`}
      role="status"
      aria-live="polite"
    >
      <Loader2 className="w-8 h-8 text-sky-600 animate-spin mb-3" />
      <h3 className="text-sm font-semibold text-slate-800">{message}</h3>
      {description && (
        <p className="text-xs text-slate-500 max-w-sm mt-1">{description}</p>
      )}
    </div>
  );
};
