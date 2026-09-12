import React from "react";
import { Activity } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="w-full bg-white border-t border-slate-200 py-6 mt-auto">
      <div className="w-full px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-lg bg-sky-600 flex items-center justify-center text-white">
            <Activity className="w-3.5 h-3.5" />
          </div>
          <span className="font-bold text-slate-900 text-sm tracking-tight">PharmaSafe-KG</span>
          <span className="text-slate-400 hidden sm:inline">|</span>
          <span className="text-slate-500 hidden sm:inline">Explainable Drug-Drug Interaction Knowledge Graph</span>
        </div>
        <p className="text-slate-400">© 2026 PharmaSafe-KG. All rights reserved.</p>
      </div>
    </footer>
  );
};
