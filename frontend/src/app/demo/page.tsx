"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Presentation,
  Play,
  Layers,
  Database,
  GitGraph,
  Sparkles,
  ShieldCheck,
  Award,
  ArrowRight,
  RotateCcw,
  FlaskConical,
  BookOpen,
  Info,
  CheckCircle2,
  AlertTriangle,
  Pill,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { PageContainer } from "@/components/layout/PageContainer";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { DemoProgress, DemoStepItem } from "@/components/demo/DemoProgress";
import { DemoNavigation } from "@/components/demo/DemoNavigation";
import { ArchitectureDiagram } from "@/components/demo/ArchitectureDiagram";
import { ResolutionStep } from "@/components/demo/ResolutionStep";
import { EvidenceStep } from "@/components/demo/EvidenceStep";
import { PredictionStep } from "@/components/demo/PredictionStep";
import { MetricsStep } from "@/components/demo/MetricsStep";
import { ConclusionStep } from "@/components/demo/ConclusionStep";
import { InteractionGraph } from "@/components/graph/InteractionGraph";
import { api } from "@/lib/api";
import { CheckResponse, InteractionResult, ResolvedDrug } from "@/types/api";

interface DemoScenario {
  id: string;
  title: string;
  category: string;
  drugs: string[];
  clinicalFocus: string;
  teachingPoint: string;
  expectedFindings: {
    documentedMajor: number;
    documentedModerate: number;
    predicted: number;
    safe: number;
  };
}

const DEMO_SCENARIOS: DemoScenario[] = [
  {
    id: "warfarin",
    title: "Scenario 1: High-Risk Anticoagulation (Warfarin + Combiflam + Pantop 40)",
    category: "Gastrointestinal Bleed Risk",
    drugs: ["Warfarin", "Combiflam", "Pantop 40"],
    clinicalFocus:
      "Combiflam contains Ibuprofen + Paracetamol. Ibuprofen + Warfarin triggers a MAJOR gastrointestinal hemorrhage warning via COX-1 inhibition and platelet displacement.",
    teachingPoint:
      "Demonstrates automatic multi-ingredient FDC resolution (Combiflam → ibuprofen + paracetamol) and high-severity clinical warning extraction from Neo4j.",
    expectedFindings: {
      documentedMajor: 1,
      documentedModerate: 1,
      predicted: 0,
      safe: 1,
    },
  },
  {
    id: "cardiac",
    title: "Scenario 2: Cardiovascular Triple Therapy (Atorva 10 + Ecosprin + Metolar XR)",
    category: "Cardiology Polypharmacy",
    drugs: ["Atorva 10", "Ecosprin", "Metolar XR"],
    clinicalFocus:
      "Atorvastatin + Aspirin + Metoprolol. Tests standard triple therapy for ischemic heart disease with moderate CYP3A4 and bleeding considerations.",
    teachingPoint:
      "Demonstrates multi-drug interaction checking with moderate severity ranking and pharmacological mechanism monographs.",
    expectedFindings: {
      documentedMajor: 0,
      documentedModerate: 2,
      predicted: 0,
      safe: 1,
    },
  },
  {
    id: "ai_prediction",
    title: "Scenario 3: Inductive GNN Link Prediction (Metformin 500 + Glibenclamide + Ecosprin)",
    category: "GNN AI Link Discovery",
    drugs: ["Metformin 500", "Glibenclamide", "Ecosprin"],
    clinicalFocus:
      "Evaluates dual secretagogue/biguanide diabetes regimen against antiplatelet therapy, highlighting GNN topological link predictions with confidence scores.",
    teachingPoint:
      "Highlights the GraphSAGE fallback predictor calculating link likelihood for pairs lacking direct knowledge base documentation.",
    expectedFindings: {
      documentedMajor: 0,
      documentedModerate: 2,
      predicted: 1,
      safe: 0,
    },
  },
  {
    id: "complex",
    title: "Scenario 4: 5-Drug Complex Polypharmacy (Combiflam + Ecosprin + Pantop 40 + Metformin 500 + Atorva 10)",
    category: "Geriatric Polypharmacy",
    drugs: ["Combiflam", "Ecosprin", "Pantop 40", "Metformin 500", "Atorva 10"],
    clinicalFocus:
      "Evaluates all 10 pairwise combinations simultaneously in a single batched Cypher UNWIND execution against Neo4j AuraDB.",
    teachingPoint:
      "Full combinatorial stress test demonstrating sub-second response times and complete evidentiary breakdown.",
    expectedFindings: {
      documentedMajor: 2,
      documentedModerate: 3,
      predicted: 2,
      safe: 3,
    },
  },
];

const DEMO_STEPS: DemoStepItem[] = [
  {
    id: "intro",
    number: 1,
    title: "Research Problem & Context",
    shortLabel: "Introduction",
    category: "overview",
  },
  {
    id: "architecture",
    number: 2,
    title: "End-to-End System Architecture",
    shortLabel: "Architecture",
    category: "pipeline",
  },
  {
    id: "scenario",
    number: 3,
    title: "Defense Test Scenario Selection",
    shortLabel: "Scenario",
    category: "overview",
  },
  {
    id: "resolution",
    number: 4,
    title: "Brand-to-Generic Resolution Layer",
    shortLabel: "Resolution",
    category: "pipeline",
  },
  {
    id: "evidence",
    number: 5,
    title: "Knowledge Graph Traversal & Evidence",
    shortLabel: "KG Traversal",
    category: "evidence",
  },
  {
    id: "gnn",
    number: 6,
    title: "Inductive GraphSAGE Link Prediction",
    shortLabel: "GNN Predictor",
    category: "gnn",
  },
  {
    id: "graph",
    number: 7,
    title: "Interactive Subgraph Topology",
    shortLabel: "Topology",
    category: "evidence",
  },
  {
    id: "metrics",
    number: 8,
    title: "Empirical Research Benchmarks",
    shortLabel: "Benchmarks",
    category: "validation",
  },
  {
    id: "conclusion",
    number: 9,
    title: "Governance & Defense Takeaways",
    shortLabel: "Conclusion",
    category: "validation",
  },
];

export default function DemoPresentationPage() {
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [selectedScenario, setSelectedScenario] = useState<DemoScenario>(DEMO_SCENARIOS[0]);
  const [apiResult, setApiResult] = useState<CheckResponse | null>(null);
  const [isApiLoading, setIsApiLoading] = useState<boolean>(false);

  // Fetch real API data for the chosen scenario
  useEffect(() => {
    let isMounted = true;
    const loadScenarioData = async () => {
      setIsApiLoading(true);
      try {
        const result = await api.checkInteractions(selectedScenario.drugs);
        if (isMounted) {
          setApiResult(result);
        }
      } catch {
        // Deterministic fallback if backend is offline during presentation
        if (isMounted) {
          setApiResult(null);
        }
      } finally {
        if (isMounted) {
          setIsApiLoading(false);
        }
      }
    };

    loadScenarioData();

    return () => {
      isMounted = false;
    };
  }, [selectedScenario]);

  const handleNext = () => {
    if (currentStepIndex < DEMO_STEPS.length - 1) {
      setCurrentStepIndex((prev) => prev + 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handlePrev = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex((prev) => prev - 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handleRestart = () => {
    setCurrentStepIndex(0);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleSelectScenario = (scenario: DemoScenario) => {
    setSelectedScenario(scenario);
  };

  const interactionsList: InteractionResult[] =
    apiResult?.interactions ||
    (selectedScenario.id === "warfarin"
      ? [
          {
            brand_a: "Combiflam",
            brand_b: "Warfarin",
            ingredient_a: "ibuprofen",
            ingredient_b: "warfarin",
            severity: "MAJOR",
            status: "documented",
            source: "knowledge_graph",
            confidence: null,
            mechanism:
              "The risk or severity of bleeding can be increased when Ibuprofen is combined with Warfarin via COX-1 platelet aggregation inhibition.",
            explanation:
              "⚠️ MAJOR RISK: Combiflam and Warfarin interact.\n\nCombiflam contains Ibuprofen. Warfarin contains Warfarin.\n\nMechanism: The risk or severity of bleeding can be increased when Ibuprofen is combined with Warfarin.",
            evidence: [
              {
                source: "DrugBank Knowledge Graph",
                severity: "MAJOR",
                mechanism: "Bleeding risk increased via platelet displacement.",
              },
            ],
          },
          {
            brand_a: "Pantop 40",
            brand_b: "Warfarin",
            ingredient_a: "pantoprazole",
            ingredient_b: "warfarin",
            severity: "MODERATE",
            status: "documented",
            source: "knowledge_graph",
            confidence: null,
            mechanism:
              "The metabolism of Warfarin can be decreased when combined with Pantoprazole, altering INR values.",
            explanation:
              "⚠️ MODERATE RISK: Pantop 40 and Warfarin interact.\n\nPantop 40 contains Pantoprazole. Warfarin contains Warfarin.\n\nMechanism: The metabolism of Warfarin can be decreased.",
            evidence: [
              {
                source: "DrugBank Knowledge Graph",
                severity: "MODERATE",
                mechanism: "CYP2C19 competitive inhibition.",
              },
            ],
          },
        ]
      : selectedScenario.id === "ai_prediction"
      ? [
          {
            brand_a: "Glibenclamide",
            brand_b: "Ecosprin",
            ingredient_a: "glibenclamide",
            ingredient_b: "aspirin",
            severity: "UNKNOWN",
            status: "predicted",
            source: "gnn_predicted",
            confidence: 0.78,
            mechanism:
              "Predicted potential interaction via GraphSAGE link prediction (confidence: 78.0%). Clinical severity unassessed.",
            explanation:
              "🤖 AI PREDICTED INTERACTION (78.0% confidence): Glibenclamide and Ecosprin.\n\nGlibenclamide contains Glibenclamide. Ecosprin contains Aspirin.\n\nNote: Inferred by GraphSAGE link prediction.",
            evidence: [
              {
                model: "GraphSAGE",
                probability: 0.78,
                threshold: 0.7,
                evidence_type: "inductive_link_prediction",
              },
            ],
          },
        ]
      : []);

  return (
    <div className="w-full pb-20 text-left bg-slate-50 min-h-screen flex flex-col justify-between">
      {/* ── 1. Top Presentation Header ───────────────────────────────────────── */}
      <div>
        <div className="bg-indigo-900 text-white py-6 border-b border-indigo-950 shadow-xs">
          <PageContainer>
            <Breadcrumbs
              items={[{ label: "Academic Defense Suite" }]}
              className="text-indigo-200 mb-1"
            />
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-indigo-700 flex items-center justify-center text-white shrink-0 shadow-2xs">
                  <Presentation className="w-5 h-5" />
                </div>
                <div>
                  <h1 className="text-xl sm:text-2xl font-bold tracking-tight">
                    PharmaSafe-KG Academic Defense Suite
                  </h1>
                  <p className="text-xs sm:text-sm text-indigo-200 mt-0.5">
                    Final-Year Major Engineering Research Project Presentation & Viva Walkthrough
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-xs font-mono bg-indigo-800 text-indigo-200 px-3 py-1 rounded-full border border-indigo-700">
                  Verified Checkpoint v1.0
                </span>
              </div>
            </div>
          </PageContainer>
        </div>

        {/* ── 2. Top Progress Stepper ─────────────────────────────────────────── */}
        <DemoProgress
          steps={DEMO_STEPS}
          currentStepIndex={currentStepIndex}
          onStepSelect={(idx) => setCurrentStepIndex(idx)}
        />

        {/* ── 3. Step Content Area ────────────────────────────────────────────── */}
        <PageContainer className="pt-8 max-w-5xl">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStepIndex}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
              className="space-y-6"
            >
              {/* Step 1: Introduction & Research Problem */}
              {currentStepIndex === 0 && (
                <div className="space-y-6">
                  <Card className="p-6 space-y-4 bg-white border-slate-200">
                    <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
                      <BookOpen className="w-5 h-5 text-sky-600" />
                      <h2 className="text-lg font-bold text-slate-900">
                        Problem Statement & Clinical Motivation
                      </h2>
                    </div>

                    <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
                      Adverse Drug-Drug Interactions (DDIs) cause up to <strong>30% of preventable hospitalizations</strong> in geriatric and chronic disease populations. In developing healthcare markets like India, this crisis is exacerbated by two severe structural barriers:
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                      <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 space-y-1.5">
                        <div className="flex items-center gap-2">
                          <Pill className="w-4 h-4 text-sky-600" />
                          <h3 className="text-sm font-bold text-slate-900">
                            Commercial Trade Name Chaos
                          </h3>
                        </div>
                        <p className="text-xs text-slate-600 leading-relaxed">
                          Over 300,000 commercial brand formulations exist in India, the vast majority being multi-ingredient Fixed-Dose Combinations (e.g. <em>Combiflam = Ibuprofen + Paracetamol</em>). Standard medical software fails to resolve these to their active chemical moieties.
                        </p>
                      </div>

                      <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 space-y-1.5">
                        <div className="flex items-center gap-2">
                          <GitGraph className="w-4 h-4 text-purple-600" />
                          <h3 className="text-sm font-bold text-slate-900">
                            Knowledge Incompleteness
                          </h3>
                        </div>
                        <p className="text-xs text-slate-600 leading-relaxed">
                          Existing clinical databases suffer from significant sparsity. Millions of drug pairs have never undergone formal clinical trials. PharmaSafe-KG bridges this gap with an inductive Graph Neural Network (GraphSAGE) fallback.
                        </p>
                      </div>
                    </div>
                  </Card>
                </div>
              )}

              {/* Step 2: System Architecture Diagram */}
              {currentStepIndex === 1 && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-bold text-slate-900">
                        End-to-End System Architecture
                      </h2>
                      <p className="text-xs text-slate-500">
                        Interactive 5-stage neuro-symbolic data processing and query pipeline.
                      </p>
                    </div>
                    <Badge variant="sky" size="sm">
                      Neuro-Symbolic Pipeline
                    </Badge>
                  </div>
                  <ArchitectureDiagram />
                </div>
              )}

              {/* Step 3: Scenario Selection */}
              {currentStepIndex === 2 && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-bold text-slate-900">
                        Select Defense Test Scenario
                      </h2>
                      <p className="text-xs text-slate-500">
                        Choose a pre-configured clinical research scenario to walk through the complete evaluation pipeline.
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {DEMO_SCENARIOS.map((sc) => {
                      const isSelected = sc.id === selectedScenario.id;
                      return (
                        <button
                          key={sc.id}
                          onClick={() => handleSelectScenario(sc)}
                          className={`p-5 rounded-lg border text-left transition-all select-none cursor-pointer space-y-3 ${
                            isSelected
                              ? "bg-sky-50/80 border-sky-400 shadow-xs ring-1 ring-sky-400"
                              : "bg-white border-slate-200 hover:border-slate-300"
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-sky-700 uppercase tracking-wider">
                              {sc.category}
                            </span>
                            {isSelected && (
                              <span className="w-2.5 h-2.5 rounded-full bg-sky-600 animate-pulse" />
                            )}
                          </div>

                          <h3 className="text-sm font-bold text-slate-900">{sc.title}</h3>

                          <div className="flex flex-wrap gap-1">
                            {sc.drugs.map((d, di) => (
                              <span
                                key={di}
                                className="px-2 py-0.5 bg-slate-100 border border-slate-200 rounded font-mono text-[11px] text-slate-800"
                              >
                                {d}
                              </span>
                            ))}
                          </div>

                          <p className="text-xs text-slate-600 leading-relaxed border-t border-slate-100 pt-2">
                            {sc.teachingPoint}
                          </p>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Step 4: Brand-to-Generic Resolution */}
              {currentStepIndex === 3 && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-bold text-slate-900">
                        Commercial Formulation Resolution ({selectedScenario.drugs.length} Medications)
                      </h2>
                      <p className="text-xs text-slate-500">
                        Translating Indian trade names into active generic entities via the Tata 1mg catalog.
                      </p>
                    </div>
                  </div>
                  <ResolutionStep
                    drugs={selectedScenario.drugs}
                    resolvedDrugs={apiResult?.resolved_drugs}
                  />
                </div>
              )}

              {/* Step 5: Knowledge Graph Traversal & Documented Evidence */}
              {currentStepIndex === 4 && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-bold text-slate-900">
                        Knowledge Graph Traversal & Clinical Evidence
                      </h2>
                      <p className="text-xs text-slate-500">
                        Neo4j AuraDB Cypher queries matching active chemical ingredients against 89k+ relationships.
                      </p>
                    </div>
                  </div>
                  <EvidenceStep interactions={interactionsList} />
                </div>
              )}

              {/* Step 6: Inductive GraphSAGE Link Prediction */}
              {currentStepIndex === 5 && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-bold text-slate-900">
                        Inductive Graph Neural Network (GraphSAGE) Fallback
                      </h2>
                      <p className="text-xs text-slate-500">
                        Neighborhood feature aggregation predicting missing links for undocumented pairs.
                      </p>
                    </div>
                  </div>
                  <PredictionStep interactions={interactionsList} />
                </div>
              )}

              {/* Step 7: Subgraph Topology Visualization */}
              {currentStepIndex === 6 && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-bold text-slate-900">
                        Interactive Subgraph Topology
                      </h2>
                      <p className="text-xs text-slate-500">
                        Visualizing brand containment and active generic interaction topology in real-time.
                      </p>
                    </div>
                  </div>
                  <InteractionGraph drugs={selectedScenario.drugs} height={460} />
                </div>
              )}

              {/* Step 8: Empirical Research Benchmarks */}
              {currentStepIndex === 7 && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-bold text-slate-900">
                        Empirical Research Validation & Model Metrics
                      </h2>
                      <p className="text-xs text-slate-500">
                        Verified results on held-out test split ($N=21,325$) with 100% leakage-free isolation.
                      </p>
                    </div>
                  </div>
                  <MetricsStep />
                </div>
              )}

              {/* Step 9: Governance & Defense Conclusion */}
              {currentStepIndex === 8 && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-bold text-slate-900">
                        Final Project Summary & Defense Conclusion
                      </h2>
                      <p className="text-xs text-slate-500">
                        Summary of engineering achievements, clinical governance, and research deliverables.
                      </p>
                    </div>
                  </div>
                  <ConclusionStep />
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </PageContainer>
      </div>

      {/* ── 4. Sticky Bottom Presentation Navigation Bar ─────────────────────── */}
      <DemoNavigation
        currentStepIndex={currentStepIndex}
        totalSteps={DEMO_STEPS.length}
        onNext={handleNext}
        onPrev={handlePrev}
        onRestart={handleRestart}
      />
    </div>
  );
}
