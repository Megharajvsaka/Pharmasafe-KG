import React from "react";

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "text" | "circular" | "rectangular" | "card";
  height?: string | number;
  width?: string | number;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  variant = "text",
  height,
  width,
  className = "",
  style,
  ...props
}) => {
  const baseStyles = "animate-pulse bg-slate-200";

  const variantStyles = {
    text: "h-4 rounded-xs w-full",
    circular: "rounded-full aspect-square",
    rectangular: "rounded-md w-full",
    card: "h-28 rounded-lg border border-slate-200 w-full",
  };

  const customStyle: React.CSSProperties = {
    height: typeof height === "number" ? `${height}px` : height,
    width: typeof width === "number" ? `${width}px` : width,
    ...style,
  };

  return (
    <div
      className={`${baseStyles} ${variantStyles[variant]} ${className}`}
      style={customStyle}
      aria-hidden="true"
      {...props}
    />
  );
};
