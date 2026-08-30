import React from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/Button";

export interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = "Query Failed",
  message,
  onRetry,
  className = "",
}) => {
  return (
    <div
      className={`p-4 bg-red-50/70 border border-red-200 rounded-lg flex items-start gap-3 text-left ${className}`}
      role="alert"
    >
      <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
      <div className="flex-1">
        <h4 className="text-sm font-semibold text-red-900">{title}</h4>
        <p className="text-xs text-red-700 mt-0.5 leading-relaxed">{message}</p>
        {onRetry && (
          <div className="mt-3">
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
              leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
              className="bg-white hover:bg-red-50 text-red-700 border-red-300"
            >
              Retry Query
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};
