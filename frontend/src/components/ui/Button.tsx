"use client";

import React, { forwardRef } from "react";
import { Loader2 } from "lucide-react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger" | "demo";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = "primary",
      size = "md",
      isLoading = false,
      disabled = false,
      leftIcon,
      rightIcon,
      className = "",
      ...props
    },
    ref
  ) => {
    const baseStyles =
      "inline-flex items-center justify-center font-medium rounded-md transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 disabled:opacity-50 disabled:cursor-not-allowed select-none active:scale-[0.99]";

    const sizeStyles = {
      sm: "text-xs px-2.5 py-1.5 gap-1.5",
      md: "text-sm px-4 py-2 gap-2",
      lg: "text-base px-5 py-2.5 gap-2.5",
    };

    const variantStyles = {
      primary:
        "bg-sky-600 hover:bg-sky-700 text-white shadow-xs focus-visible:outline-sky-600 border border-transparent",
      secondary:
        "bg-slate-100 hover:bg-slate-200 text-slate-800 focus-visible:outline-slate-600 border border-slate-200",
      outline:
        "bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 shadow-xs focus-visible:outline-sky-600",
      ghost:
        "bg-transparent hover:bg-slate-100 text-slate-700 focus-visible:outline-slate-600",
      danger:
        "bg-red-600 hover:bg-red-700 text-white shadow-xs focus-visible:outline-red-600 border border-transparent",
      demo:
        "bg-indigo-600 hover:bg-indigo-700 text-white shadow-xs focus-visible:outline-indigo-600 border border-transparent",
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
        {...props}
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 animate-spin text-current" />
        ) : (
          leftIcon
        )}
        <span>{children}</span>
        {!isLoading && rightIcon}
      </button>
    );
  }
);

Button.displayName = "Button";
