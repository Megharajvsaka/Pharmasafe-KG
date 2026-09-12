"use client";

import React from "react";
import Link from "next/link";
import {
  ArrowRight,
  ShieldAlert,
  GitGraph,
  Database,
  FileCheck,
} from "lucide-react";
import { motion } from "framer-motion";
import { PageContainer } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { slideUp } from "@/lib/motion";
import { useAuth } from "@/context/AuthContext";

export default function HomePage() {
  const { isAuthenticated } = useAuth();

  const metrics = [
    { label: "Total Graph Nodes", value: "50,073", subtext: "2,073 Ingredients + 48,000 Brands" },
    { label: "DDI Relationships", value: "89,367", subtext: "Calibrated Severity Evidence" },
    { label: "Mapped Indian Brands", value: "304,404", subtext: "1,002 Standardized Generics" },
    { label: "GraphSAGE Test AUC", value: "0.8834", subtext: "Leakage-Free Evaluation (N=21,325)" },
  ];

  const pillars = [
    {
      title: "Indian Brand-to-Generic Resolution",
      desc: "Maps over 304,000 commercial formulations to standardized INN generic entities. Resolves multi-ingredient fixed-dose combinations (e.g. Combiflam → ibuprofen + paracetamol).",
      badge: "304k+ Formulations",
      icon: <FileCheck className="w-6 h-6 text-sky-600" />,
    },
    {
      title: "Neo4j AuraDB Knowledge Graph",
      desc: "A production graph database indexing 50,073 nodes and 160,879 relationships. Stores calibrated severity tiers (Major 22.9%, Moderate 72.8%, Minor 4.3%) and pharmacological mechanism descriptions.",
      badge: "160k+ Relationships",
      icon: <Database className="w-6 h-6 text-emerald-600" />,
    },
    {
      title: "Inductive GraphSAGE Link Prediction",
      desc: "A 3-layer Graph Neural Network trained strictly on leakage-free train edge indices. Generalizes to unindexed drug combinations by aggregating local neighborhood topological embeddings.",
      badge: "AUC = 0.8834",
      icon: <GitGraph className="w-6 h-6 text-purple-600" />,
    },
    {
      title: "Epistemic AI Transparency",
      desc: "Maintains a strict clinical boundary between verified Knowledge Graph facts and statistical GNN predictions. Predicted pairs are clearly labeled with confidence percentages and unassessed severity.",
      badge: "Clinical Safety",
      icon: <ShieldAlert className="w-6 h-6 text-amber-600" />,
    },
  ];

  return (
    <div className="w-full pb-16">
      {/* ── HERO SECTION ──────────────────────────────────────────────────────── */}
      <div className="bg-white border-b border-slate-200 pt-16 pb-20">
        <PageContainer>
          <motion.div
            initial="hidden"
            animate="visible"
            variants={slideUp}
            className="max-w-3xl mx-auto text-center space-y-6"
          >
            {/* Main Headline */}
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight">
              Explainable Knowledge Graph + GNN for Drug Interaction Detection
            </h1>

            {/* Subtitle / Value Statement */}
            <p className="text-base sm:text-lg text-slate-600 leading-relaxed max-w-2xl mx-auto">
              Automated Indian brand-to-generic formulation resolution, Neo4j Knowledge Graph traversal,
              and inductive GraphSAGE link prediction for multi-drug polypharmacy safety.
            </p>

            {/* Single Primary Call-to-Action */}
            <div className="flex items-center justify-center pt-3">
              <Link href={isAuthenticated ? "/dashboard" : "/auth/register"}>
                <Button
                  size="lg"
                  variant="primary"
                  rightIcon={<ArrowRight className="w-4 h-4" />}
                  className="px-8 py-3.5 text-base font-semibold shadow-sm"
                >
                  {isAuthenticated ? "Go to Dashboard" : "Get Started"}
                </Button>
              </Link>
            </div>
          </motion.div>
        </PageContainer>
      </div>

      {/* ── METRICS TICKER SECTION ────────────────────────────────────────────── */}
      <div className="bg-slate-100/70 border-b border-slate-200 py-6">
        <PageContainer>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {metrics.map((m, idx) => (
              <div
                key={idx}
                className="p-4 bg-white rounded-lg border border-slate-200 shadow-2xs text-center"
              >
                <div className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight font-mono">
                  {m.value}
                </div>
                <div className="text-xs font-semibold text-slate-700 uppercase tracking-wider mt-1">
                  {m.label}
                </div>
                <div className="text-[11px] text-slate-400 mt-0.5">{m.subtext}</div>
              </div>
            ))}
          </div>
        </PageContainer>
      </div>

      {/* ── SYSTEM CAPABILITIES ──────────────────────────────────────────────── */}
      <PageContainer>
        <div className="pt-16 pb-8 text-left">
          <div className="max-w-2xl mb-10">
            <Badge variant="sky" size="sm" className="mb-2">
              System Capabilities
            </Badge>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Bridging Commercial Indian Pharmacy & Pharmacological Science
            </h2>
            <p className="text-sm text-slate-600 mt-2 leading-relaxed">
              Standard clinical DDI tools only accept international chemical identifiers.
              PharmaSafe-KG bridges this gap by combining commercial retail catalogs with
              graph-structured pharmacology.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {pillars.map((p, idx) => (
              <Card key={idx} className="p-6 text-left flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-center">
                      {p.icon}
                    </div>
                    <Badge variant="neutral" size="sm">
                      {p.badge}
                    </Badge>
                  </div>
                  <h3 className="text-base font-bold text-slate-900 mb-2">{p.title}</h3>
                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">{p.desc}</p>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </PageContainer>
    </div>
  );
}
