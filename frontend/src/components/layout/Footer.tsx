import React from "react";
import Link from "next/link";
import { Activity, ShieldCheck, Database, FileText } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="w-full bg-white border-t border-slate-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8 text-left">
          {/* Col 1: Project Identity */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-sky-600 flex items-center justify-center text-white">
                <Activity className="w-4 h-4" />
              </div>
              <span className="font-bold text-slate-900 text-sm">PharmaSafe-KG</span>
              <span className="text-xs text-slate-400">| Final-Year Research Project</span>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed max-w-md">
              An explainable Knowledge Graph + Inductive Graph Neural Network (GraphSAGE) system
              for Drug-Drug Interaction detection, Indian brand-to-generic drug resolution, and
              polypharmacy analysis.
            </p>
            <div className="flex items-center gap-4 text-xs text-slate-600 pt-1">
              <span className="flex items-center gap-1">
                <Database className="w-3.5 h-3.5 text-slate-400" />
                Neo4j AuraDB (50,073 nodes)
              </span>
              <span className="flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                GraphSAGE (0.8834 AUC)
              </span>
            </div>
          </div>

          {/* Col 2: Navigation Links */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider">
              Navigation
            </h4>
            <ul className="space-y-1.5 text-xs text-slate-600">
              <li>
                <Link href="/" className="hover:text-sky-600 transition-colors">
                  Overview & Platform
                </Link>
              </li>
              <li>
                <Link href="/analyze" className="hover:text-sky-600 transition-colors">
                  Medication Workbench
                </Link>
              </li>
              <li>
                <Link href="/demo" className="hover:text-indigo-600 font-medium transition-colors">
                  Academic Defense Demo
                </Link>
              </li>
              <li>
                <Link href="/about" className="hover:text-sky-600 transition-colors">
                  Model Card & Provenance
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 3: Research Metadata */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-slate-900 uppercase tracking-wider">
              Research & Specs
            </h4>
            <ul className="space-y-1.5 text-xs text-slate-600">
              <li className="flex items-center gap-1">
                <FileText className="w-3.5 h-3.5 text-slate-400" />
                <span>IEEE Manuscript Ready</span>
              </li>
              <li>
                <span className="text-slate-500">Benchmark:</span> DrugBank + 1mg Catalog
              </li>
              <li>
                <span className="text-slate-500">Pipeline:</span> Leakage-Free Link Pred
              </li>
              <li>
                <span className="text-slate-500">Version:</span> v1.0-p1-verified
              </li>
            </ul>
          </div>
        </div>

        {/* Clinical Disclaimer Banner */}
        <div className="p-3 bg-slate-50 rounded-md border border-slate-200 text-left mb-6">
          <p className="text-[11px] text-slate-500 leading-relaxed">
            <strong className="text-slate-700 font-semibold">Clinical & Research Disclaimer:</strong>{" "}
            PharmaSafe-KG is an academic research platform designed for computational pharmacological analysis.
            Absence of a documented interaction does not imply clinical safety. Always consult certified
            pharmacopoeia and clinical specialists for medical decision-making.
          </p>
        </div>

        {/* Copyright */}
        <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-400">
          <p>© 2026 PharmaSafe-KG. Final-Year Major Engineering Project.</p>
          <p>All research models and Knowledge Graph data verified leakage-free.</p>
        </div>
      </div>
    </footer>
  );
};
