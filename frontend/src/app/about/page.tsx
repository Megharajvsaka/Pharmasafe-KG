import React from "react";
import Link from "next/link";
import {
  BookOpen,
  Database,
  GitGraph,
  ShieldCheck,
  CheckCircle2,
  FileText,
  Layers,
  ArrowRight,
} from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

export default function AboutPage() {
  return (
    <div className="w-full pb-16 text-left">
      {/* Top Header */}
      <div className="bg-white border-b border-slate-200 py-6">
        <PageContainer>
          <Breadcrumbs items={[{ label: "Research Methodology & Model Card" }]} className="mb-2" />
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-sky-600 flex items-center justify-center text-white">
              <BookOpen className="w-4 h-4" />
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              Research Methodology & Model Specifications
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Formal architectural documentation, data lineage, and leakage-free GraphSAGE evaluation results.
          </p>
        </PageContainer>
      </div>

      <PageContainer className="pt-8 space-y-8">
        {/* Section 1: System Overview */}
        <Card className="p-6">
          <h2 className="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2">
            <Layers className="w-5 h-5 text-sky-600" />
            <span>PharmaSafe-KG Architecture</span>
          </h2>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed mb-4">
            PharmaSafe-KG is an explainable biomedical Knowledge Graph (KG) and Graph Neural Network (GNN)
            system addressing the challenge of drug-drug interaction detection in commercial multi-ingredient
            formulations.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
            <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-1">
                Data Provenance
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                92,161 DDI pairs from DrugBank joined with 304,404 Indian medicine formulations (Tata 1mg
                catalog) mapped to 1,002 standardized active generic entities.
              </p>
            </div>

            <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-1">
                Knowledge Graph
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Neo4j AuraDB instance holding 50,073 nodes (2,073 generic Ingredients + 48,000 brand Drugs)
                and 160,879 relationships.
              </p>
            </div>

            <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-1">
                GNN Link Predictor
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Inductive 3-layer GraphSAGE architecture predicting missing links based on structural
                neighborhood aggregations.
              </p>
            </div>
          </div>
        </Card>

        {/* Section 2: Model Card */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <GitGraph className="w-5 h-5 text-purple-600" />
              <span>Model Card: GraphSAGE-DDI (Mitchell et al. Framework)</span>
            </h2>
            <Badge variant="predicted" size="sm">
              Version 1.0
            </Badge>
          </div>

          <div className="space-y-4 text-xs sm:text-sm text-slate-700">
            <div>
              <h4 className="font-semibold text-slate-900">Model Architecture</h4>
              <p className="text-xs text-slate-500 mt-0.5">
                Input features ($d=10$) → SAGEConv(128) + ReLU + Dropout(0.3) + BatchNorm → SAGEConv(64) +
                ReLU + Dropout(0.3) + BatchNorm → SAGEConv(32) → Dot-Product Decoder → Sigmoid link probability.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div className="p-3 bg-slate-50 rounded border border-slate-200">
                <span className="font-semibold text-slate-900 block mb-1">Leakage-Free Splitting</span>
                <p className="text-xs text-slate-500">
                  Message-passing graph ($129,024$ directed edges) constructed strictly from 70% positive
                  training edges ($N=64,512$). Test edges are strictly excluded from message passing.
                </p>
              </div>

              <div className="p-3 bg-slate-50 rounded border border-slate-200">
                <span className="font-semibold text-slate-900 block mb-1">Evaluation Metrics</span>
                <p className="text-xs text-slate-500">
                  Held-out Test Set ($N=21,325$): ROC-AUC = <strong>0.8834</strong>, F1-Score ={" "}
                  <strong>0.8330</strong>, Precision = <strong>0.7215</strong>, Recall = <strong>0.9851</strong>.
                </p>
              </div>
            </div>
          </div>
        </Card>

        {/* Action Button */}
        <div className="flex justify-end gap-3">
          <Link href="/dashboard?tab=analyse">
            <Button variant="primary" rightIcon={<ArrowRight className="w-4 h-4" />}>
              Open Medication Workbench
            </Button>
          </Link>
        </div>
      </PageContainer>
    </div>
  );
}
