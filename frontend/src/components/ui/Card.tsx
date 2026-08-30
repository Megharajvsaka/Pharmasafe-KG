import React from "react";
import { SeverityLevel } from "@/types/api";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  accent?: "major" | "moderate" | "minor" | "predicted" | "safe" | "none";
  severity?: SeverityLevel;
  interactive?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  accent = "none",
  severity,
  interactive = false,
  className = "",
  ...props
}) => {
  let activeAccent = accent;

  if (severity) {
    switch (severity) {
      case "MAJOR":
        activeAccent = "major";
        break;
      case "MODERATE":
        activeAccent = "moderate";
        break;
      case "MINOR":
        activeAccent = "minor";
        break;
      case "UNKNOWN":
      case "UNASSESSED":
        activeAccent = "predicted";
        break;
      default:
        activeAccent = "none";
    }
  }

  const baseStyles = "bg-white rounded-lg border border-slate-200 shadow-xs p-4 transition-all";

  const accentStyles = {
    none: "",
    major: "border-l-4 border-l-red-600 bg-red-50/20",
    moderate: "border-l-4 border-l-amber-500 bg-amber-50/20",
    minor: "border-l-4 border-l-emerald-600 bg-emerald-50/20",
    predicted: "border-l-4 border-l-purple-600 bg-purple-50/20",
    safe: "border-l-4 border-l-slate-400 bg-slate-50/50",
  };

  const interactiveStyles = interactive
    ? "hover:border-slate-300 hover:shadow-sm cursor-pointer"
    : "";

  return (
    <div
      className={`${baseStyles} ${accentStyles[activeAccent]} ${interactiveStyles} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
