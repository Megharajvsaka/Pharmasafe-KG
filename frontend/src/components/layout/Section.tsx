import React from "react";

export interface SectionProps {
  title?: string;
  subtitle?: string;
  badge?: React.ReactNode;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export const Section: React.FC<SectionProps> = ({
  title,
  subtitle,
  badge,
  action,
  children,
  className = "",
}) => {
  return (
    <section className={`py-8 ${className}`}>
      {(title || subtitle || badge || action) && (
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-6 text-left">
          <div>
            {badge && <div className="mb-2">{badge}</div>}
            {title && (
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                {title}
              </h2>
            )}
            {subtitle && (
              <p className="text-sm text-slate-500 mt-1 max-w-2xl leading-relaxed">
                {subtitle}
              </p>
            )}
          </div>
          {action && <div className="shrink-0">{action}</div>}
        </div>
      )}
      {children}
    </section>
  );
};
