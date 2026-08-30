import React from "react";

export interface DividerProps {
  label?: string;
  className?: string;
}

export const Divider: React.FC<DividerProps> = ({ label, className = "" }) => {
  if (label) {
    return (
      <div className={`relative flex items-center my-4 ${className}`}>
        <div className="flex-grow border-t border-slate-200" />
        <span className="flex-shrink mx-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          {label}
        </span>
        <div className="flex-grow border-t border-slate-200" />
      </div>
    );
  }

  return <hr className={`my-4 border-t border-slate-200 ${className}`} />;
};
