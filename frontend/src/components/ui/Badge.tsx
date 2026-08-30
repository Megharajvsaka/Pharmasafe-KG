import React from "react";
import { SeverityLevel } from "@/types/api";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?:
    | "major"
    | "moderate"
    | "minor"
    | "predicted"
    | "documented"
    | "safe"
    | "neutral"
    | "sky";
  severity?: SeverityLevel;
  size?: "sm" | "md";
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant,
  severity,
  size = "md",
  className = "",
  ...props
}) => {
  let activeVariant = variant || "neutral";

  if (severity) {
    switch (severity) {
      case "MAJOR":
        activeVariant = "major";
        break;
      case "MODERATE":
        activeVariant = "moderate";
        break;
      case "MINOR":
        activeVariant = "minor";
        break;
      case "UNKNOWN":
      case "UNASSESSED":
        activeVariant = "predicted";
        break;
      default:
        activeVariant = "neutral";
    }
  }

  const baseStyles =
    "inline-flex items-center font-semibold rounded-full uppercase tracking-wider select-none border";

  const sizeStyles = {
    sm: "text-[10px] px-2 py-0.5 leading-tight",
    md: "text-xs px-2.5 py-1 leading-snug",
  };

  const variantStyles = {
    major: "bg-red-50 text-red-800 border-red-300",
    moderate: "bg-amber-50 text-amber-900 border-amber-300",
    minor: "bg-emerald-50 text-emerald-800 border-emerald-300",
    predicted: "bg-purple-50 text-purple-900 border-purple-300",
    documented: "bg-emerald-50 text-emerald-900 border-emerald-300",
    safe: "bg-slate-100 text-slate-700 border-slate-300",
    neutral: "bg-slate-100 text-slate-700 border-slate-200",
    sky: "bg-sky-50 text-sky-800 border-sky-200",
  };

  return (
    <span
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[activeVariant]} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
};
