"use client";

import React, { useState, useEffect, useRef, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  GitGraph,
  ZoomIn,
  ZoomOut,
  Maximize2,
  RefreshCw,
  Search,
  Plus,
  Trash2,
  ExternalLink,
  Info,
  Loader2,
  AlertCircle,
  FlaskConical,
  Pill,
  ArrowRight,
  Layers,
  Sparkles,
} from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { DrugSearchBar } from "@/components/drugs/DrugSearchBar";
import { DrugChip } from "@/components/drugs/DrugChip";
import { ErrorState } from "@/components/feedback/ErrorState";
import { EmptyState } from "@/components/feedback/EmptyState";
import { useToast } from "@/components/feedback/Toast";
import { api, ApiClientError } from "@/lib/api";
import { GraphResponse, GraphNode, GraphEdge } from "@/types/api";
import { useAnalysis } from "@/context/AnalysisContext";

interface NodePosition {
  x: number;
  y: number;
}

function GraphExplorerContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { showToast } = useToast();
  const { loadPreset } = useAnalysis();

  // Initial drugs from query string or default preset
  const [selectedDrugs, setSelectedDrugs] = useState<string[]>(() => {
    const queryDrugs = searchParams.getAll("drugs");
    if (queryDrugs.length > 0) {
      return Array.from(new Set(queryDrugs.map((d) => d.trim()).filter(Boolean))).slice(0, 10);
    }
    return ["Warfarin", "Combiflam", "Pantop 40"];
  });

  const [graphData, setGraphData] = useState<GraphResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  // Canvas viewport transform states
  const [zoom, setZoom] = useState<number>(1);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [nodePositions, setNodePositions] = useState<Record<string, NodePosition>>({});

  const containerRef = useRef<HTMLDivElement>(null);
  const isDraggingRef = useRef(false);
  const dragStartRef = useRef({ x: 0, y: 0 });

  const presets = [
    { label: "Warfarin Regimen", drugs: ["Warfarin", "Combiflam", "Pantop 40"] },
    { label: "Cardio Triple", drugs: ["Atorva 10", "Ecosprin", "Metolar XR"] },
    { label: "Diabetes Regimen", drugs: ["Metformin 500", "Glibenclamide", "Ecosprin"] },
    { label: "5-Drug Complex", drugs: ["Combiflam", "Ecosprin", "Pantop 40", "Metformin 500", "Atorva 10"] },
  ];

  const fetchGraphData = async (drugs: string[]) => {
    if (drugs.length < 2) {
      setGraphData(null);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    setSelectedNode(null);

    try {
      const data = await api.getGraph(drugs);
      setGraphData(data);

      // Layout algorithm: Circular bipartite placement
      const positions: Record<string, NodePosition> = {};
      const brandNodes = data.nodes.filter((n) => n.type === "Drug");
      const ingNodes = data.nodes.filter((n) => n.type === "Ingredient");

      const centerX = 380;
      const centerY = 260;

      // Outer ring for brand formulations
      const brandRadius = 180;
      brandNodes.forEach((node, i) => {
        const angle = (2 * Math.PI * i) / (brandNodes.length || 1);
        positions[node.id] = {
          x: centerX + brandRadius * Math.cos(angle),
          y: centerY + brandRadius * Math.sin(angle),
        };
      });

      // Inner ring for generic ingredients
      const ingRadius = 90;
      ingNodes.forEach((node, i) => {
        const angle = (2 * Math.PI * i) / (ingNodes.length || 1) + Math.PI / 6;
        positions[node.id] = {
          x: centerX + ingRadius * Math.cos(angle),
          y: centerY + ingRadius * Math.sin(angle),
        };
      });

      setNodePositions(positions);
    } catch (err) {
      const msg =
        err instanceof ApiClientError ? err.detail : "Failed to load knowledge graph topology.";
      setError(msg);
      setGraphData(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchGraphData(selectedDrugs);
  }, [selectedDrugs]);

  const handleAddDrug = (name: string) => {
    const clean = name.trim();
    if (!clean) return;
    if (selectedDrugs.length >= 10) {
      showToast("error", "Limit Reached", "Maximum 10 medications supported in graph explorer.");
      return;
    }
    if (selectedDrugs.some((d) => d.toLowerCase() === clean.toLowerCase())) {
      showToast("info", "Already Added", `"${clean}" is already in the explorer.`);
      return;
    }
    setSelectedDrugs((prev) => [...prev, clean]);
  };

  const handleRemoveDrug = (name: string) => {
    setSelectedDrugs((prev) => prev.filter((d) => d.toLowerCase() !== name.toLowerCase()));
  };

  const handleClearAll = () => {
    setSelectedDrugs([]);
    setGraphData(null);
    setSelectedNode(null);
  };

  const handleLoadPreset = (presetDrugs: string[]) => {
    setSelectedDrugs([...presetDrugs]);
    showToast("info", "Regimen Loaded", `Loaded ${presetDrugs.length} medications into graph.`);
  };

  const handleSendToWorkbench = () => {
    loadPreset(selectedDrugs);
    router.push("/analyze");
  };

  // Canvas Pan & Zoom Handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    isDraggingRef.current = true;
    dragStartRef.current = { x: e.clientX - pan.x, y: e.clientY - pan.y };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDraggingRef.current) return;
    setPan({
      x: e.clientX - dragStartRef.current.x,
      y: e.clientY - dragStartRef.current.y,
    });
  };

  const handleMouseUp = () => {
    isDraggingRef.current = false;
  };

  const handleZoomIn = () => setZoom((z) => Math.min(z + 0.2, 2.5));
  const handleZoomOut = () => setZoom((z) => Math.max(z - 0.2, 0.4));
  const handleResetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    setSelectedNode(null);
  };

  // Connected edges for selected node
  const connectedEdges = graphData?.edges.filter(
    (e) => selectedNode && (e.from === selectedNode.id || e.to === selectedNode.id)
  ) || [];

  return (
    <div className="w-full pb-16 text-left">
      {/* ── Top Header ───────────────────────────────────────────────────────── */}
      <div className="bg-white border-b border-slate-200 py-6">
        <PageContainer>
          <Breadcrumbs
            items={[
              { label: "Medication Workbench", href: "/analyze" },
              { label: "Knowledge Graph Explorer" },
            ]}
            className="mb-2"
          />
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-sky-600 flex items-center justify-center text-white">
                  <GitGraph className="w-5 h-5" />
                </div>
                <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                  Biomedical Knowledge Graph Explorer
                </h1>
              </div>
              <p className="text-xs sm:text-sm text-slate-500 mt-1">
                Visualizing commercial brand containment links and peer-reviewed interaction topologies from Neo4j AuraDB.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="primary"
                size="sm"
                onClick={handleSendToWorkbench}
                disabled={selectedDrugs.length < 2}
                leftIcon={<FlaskConical className="w-4 h-4" />}
              >
                Evaluate in Workbench
              </Button>
            </div>
          </div>
        </PageContainer>
      </div>

      <PageContainer className="pt-8 space-y-6">
        {/* ── Search & Preset Bar ────────────────────────────────────────────── */}
        <Card className="p-4 sm:p-5 space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-center">
            {/* Search Input (7 cols) */}
            <div className="lg:col-span-7">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1.5">
                Add Medication to Visualizer ({selectedDrugs.length}/10)
              </span>
              <DrugSearchBar
                onSelectDrug={handleAddDrug}
                disabled={isLoading}
                maxReached={selectedDrugs.length >= 10}
              />
            </div>

            {/* Presets (5 cols) */}
            <div className="lg:col-span-5">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-1.5">
                Quick Preset Subgraphs
              </span>
              <div className="grid grid-cols-2 gap-1.5">
                {presets.map((p, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleLoadPreset(p.drugs)}
                    className="p-1.5 px-2.5 text-left text-xs bg-slate-50 hover:bg-sky-50 border border-slate-200 hover:border-sky-300 rounded font-medium text-slate-800 transition-colors select-none cursor-pointer"
                  >
                    <span className="font-semibold block truncate">{p.label}</span>
                    <span className="text-[10px] text-slate-400">{p.drugs.length} drugs</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Active Drugs Chips */}
          {selectedDrugs.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5 pt-3 border-t border-slate-100">
              <span className="text-xs font-semibold text-slate-600 mr-1">Active Subgraph Nodes:</span>
              {selectedDrugs.map((drug, idx) => (
                <DrugChip
                  key={`${drug}-${idx}`}
                  name={drug}
                  index={idx}
                  onRemove={handleRemoveDrug}
                  disabled={isLoading}
                />
              ))}
              <button
                type="button"
                onClick={handleClearAll}
                className="text-xs text-red-600 hover:text-red-800 font-medium ml-2 cursor-pointer flex items-center gap-1"
              >
                <Trash2 className="w-3 h-3" />
                <span>Clear</span>
              </button>
            </div>
          )}
        </Card>

        {/* ── Main Graph Canvas Viewport ─────────────────────────────────────── */}
        <Card className="p-0 overflow-hidden bg-white border-slate-200">
          {/* Canvas Controls Header */}
          <div className="px-4 py-3 border-b border-slate-200 bg-slate-50 flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <GitGraph className="w-4 h-4 text-sky-600" />
              <h2 className="text-xs sm:text-sm font-bold text-slate-900">
                {graphData ? (
                  <>
                    Active Subgraph ({graphData.nodes.length} Nodes, {graphData.edges.length} Edges)
                  </>
                ) : (
                  "Graph Topology"
                )}
              </h2>
            </div>

            {/* Toolbar Buttons */}
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={handleZoomIn}
                className="p-1.5 rounded text-slate-600 hover:text-slate-900 hover:bg-slate-200 transition-colors cursor-pointer"
                title="Zoom In"
                aria-label="Zoom in"
              >
                <ZoomIn className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={handleZoomOut}
                className="p-1.5 rounded text-slate-600 hover:text-slate-900 hover:bg-slate-200 transition-colors cursor-pointer"
                title="Zoom Out"
                aria-label="Zoom out"
              >
                <ZoomOut className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={handleResetView}
                className="p-1.5 rounded text-slate-600 hover:text-slate-900 hover:bg-slate-200 transition-colors cursor-pointer"
                title="Reset View"
                aria-label="Reset view"
              >
                <Maximize2 className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => fetchGraphData(selectedDrugs)}
                className="p-1.5 rounded text-slate-600 hover:text-slate-900 hover:bg-slate-200 transition-colors cursor-pointer"
                title="Refresh Graph"
                aria-label="Refresh graph"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* SVG Viewport */}
          <div
            ref={containerRef}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            className="w-full h-[540px] bg-slate-50/50 relative cursor-grab active:cursor-grabbing select-none overflow-hidden"
          >
            {isLoading ? (
              <div className="w-full h-full flex flex-col items-center justify-center">
                <Loader2 className="w-8 h-8 text-sky-600 animate-spin mb-2" />
                <p className="text-xs font-semibold text-slate-700">Querying Neo4j AuraDB...</p>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  Traversing formulation hierarchies and DDI edges
                </p>
              </div>
            ) : error ? (
              <div className="w-full h-full flex flex-col items-center justify-center p-6">
                <AlertCircle className="w-8 h-8 text-red-500 mb-2" />
                <p className="text-sm font-bold text-slate-800">Unable to Load Graph</p>
                <p className="text-xs text-slate-500 mt-1 max-w-sm text-center">{error}</p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => fetchGraphData(selectedDrugs)}
                  className="mt-4"
                >
                  Retry Query
                </Button>
              </div>
            ) : !graphData || graphData.nodes.length === 0 ? (
              <div className="w-full h-full flex flex-col items-center justify-center p-6">
                <Info className="w-8 h-8 text-slate-400 mb-2" />
                <p className="text-sm font-bold text-slate-800">No Graph Data Available</p>
                <p className="text-xs text-slate-500 mt-1">
                  Add at least 2 medications to construct an interaction subgraph.
                </p>
              </div>
            ) : (
              <svg width="100%" height="100%" viewBox="0 0 760 520" className="w-full h-full">
                <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
                  {/* Draw Edges */}
                  {graphData.edges.map((edge, idx) => {
                    const posFrom = nodePositions[edge.from];
                    const posTo = nodePositions[edge.to];
                    if (!posFrom || !posTo) return null;

                    const isContains = edge.label === "CONTAINS";
                    const strokeColor = isContains
                      ? "#94A3B8"
                      : edge.color || (edge.label === "MAJOR" ? "#DC2626" : "#D97706");
                    const strokeWidth = isContains ? 1.5 : Math.max(edge.width || 2, 2.5);
                    const isDashed = edge.label?.toLowerCase().includes("predicted");

                    return (
                      <g key={`edge-${idx}`}>
                        <line
                          x1={posFrom.x}
                          y1={posFrom.y}
                          x2={posTo.x}
                          y2={posTo.y}
                          stroke={strokeColor}
                          strokeWidth={strokeWidth}
                          strokeDasharray={isDashed ? "4,4" : undefined}
                          strokeOpacity={0.8}
                        />
                        {!isContains && (
                          <text
                            x={(posFrom.x + posTo.x) / 2}
                            y={(posFrom.y + posTo.y) / 2 - 4}
                            fill={strokeColor}
                            fontSize="9"
                            fontWeight="600"
                            textAnchor="middle"
                            className="font-mono select-none"
                          >
                            {edge.label}
                          </text>
                        )}
                      </g>
                    );
                  })}

                  {/* Draw Nodes */}
                  {graphData.nodes.map((node) => {
                    const pos = nodePositions[node.id];
                    if (!pos) return null;

                    const isDrug = node.type === "Drug";
                    const isSelected = selectedNode?.id === node.id;
                    const radius = isDrug ? 18 : 14;
                    const fill = isDrug ? "#0284C7" : "#059669";

                    return (
                      <g
                        key={`node-${node.id}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedNode(node);
                        }}
                        className="cursor-pointer"
                      >
                        {isSelected && (
                          <circle
                            cx={pos.x}
                            cy={pos.y}
                            r={radius + 5}
                            fill="none"
                            stroke="#0284C7"
                            strokeWidth="2.5"
                            strokeDasharray="3,3"
                          />
                        )}

                        <circle
                          cx={pos.x}
                          cy={pos.y}
                          r={radius}
                          fill={fill}
                          stroke="#FFFFFF"
                          strokeWidth="2"
                          className="shadow-md transition-transform hover:scale-110"
                        />

                        <text
                          x={pos.x}
                          y={pos.y + radius + 13}
                          textAnchor="middle"
                          fill="#0F172A"
                          fontSize="10"
                          fontWeight="600"
                          className="select-none font-sans"
                        >
                          {node.label}
                        </text>
                      </g>
                    );
                  })}
                </g>
              </svg>
            )}

            {/* Selected Node Details Drawer */}
            {selectedNode && (
              <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-xs p-4 rounded-lg border border-slate-200 shadow-lg max-w-xs text-xs space-y-2.5 animate-in fade-in zoom-in-95 duration-150">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                  <div>
                    <span className="font-bold text-slate-900 text-sm block">
                      {selectedNode.label}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">ID: {selectedNode.id}</span>
                  </div>
                  <span
                    className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                      selectedNode.type === "Drug"
                        ? "bg-sky-100 text-sky-800"
                        : "bg-emerald-100 text-emerald-800"
                    }`}
                  >
                    {selectedNode.type === "Drug" ? "Brand Formulation" : "Generic Chemical"}
                  </span>
                </div>

                <div>
                  <span className="font-semibold text-slate-700 text-[11px] block mb-1">
                    Connected Relationships ({connectedEdges.length}):
                  </span>
                  <div className="space-y-1 max-h-28 overflow-y-auto pr-1">
                    {connectedEdges.map((edge, i) => (
                      <div
                        key={i}
                        className="p-1.5 bg-slate-50 rounded border border-slate-200 text-[10px] flex items-center justify-between"
                      >
                        <span className="font-mono text-slate-600 truncate max-w-[140px]">
                          {edge.from === selectedNode.id ? `→ ${edge.to}` : `← ${edge.from}`}
                        </span>
                        <span className="font-semibold text-slate-800">{edge.label}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-100 flex gap-2">
                  <Link
                    href={`/drugs/${encodeURIComponent(selectedNode.label)}`}
                    className="w-full"
                  >
                    <Button variant="outline" size="sm" className="w-full text-xs">
                      <span>View Monograph</span>
                      <ExternalLink className="w-3 h-3 ml-1" />
                    </Button>
                  </Link>
                </div>
              </div>
            )}
          </div>

          {/* Clinical Legend */}
          <div className="px-4 py-3 bg-slate-50 border-t border-slate-200 flex flex-wrap items-center justify-between gap-4 text-xs text-slate-600">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-full bg-sky-600" />
                <span className="font-medium text-slate-900">Commercial Brand Formulation</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-full bg-emerald-600" />
                <span className="font-medium text-slate-900">Active Generic Chemical</span>
              </span>
            </div>

            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 bg-slate-400" />
                <span>CONTAINS</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 bg-red-600" />
                <span className="font-semibold text-red-700">MAJOR DDI</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 bg-amber-500" />
                <span className="font-semibold text-amber-700">MODERATE DDI</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 border-t border-dashed border-purple-600" />
                <span className="font-semibold text-purple-700">AI Predicted Link</span>
              </span>
            </div>
          </div>
        </Card>
      </PageContainer>
    </div>
  );
}

export default function GraphPage() {
  return (
    <Suspense
      fallback={
        <div className="w-full py-16 text-center">
          <Loader2 className="w-8 h-8 text-sky-600 animate-spin mx-auto mb-2" />
          <p className="text-xs text-slate-500 font-semibold">Loading Knowledge Graph Explorer...</p>
        </div>
      }
    >
      <GraphExplorerContent />
    </Suspense>
  );
}
