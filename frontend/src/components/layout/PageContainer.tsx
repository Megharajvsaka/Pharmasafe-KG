import React from "react";

export interface PageContainerProps {
  children: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl" | "full";
  className?: string;
}

export const PageContainer: React.FC<PageContainerProps> = ({
  children,
  size = "lg",
  className = "",
}) => {
  const sizeStyles = {
    sm: "max-w-3xl",
    md: "max-w-5xl",
    lg: "max-w-7xl",
    xl: "max-w-[1400px]",
    full: "max-w-full",
  };

  return (
    <div className={`w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 ${sizeStyles[size]} ${className}`}>
      {children}
    </div>
  );
};
