"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  GitGraph,
  ZoomIn,
  ZoomOut,
  Maximize2,
  RefreshCw,
  Info,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { api } from "@/lib/api";
import { GraphResponse, GraphNode, GraphEdge } from "@/types/api";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export interface InteractionGraphProps {
  drugs: string[];
  height?: string | number;
  className?: string;
}

interface NodePosition {
  x: number;
  y: number;
  vx: number;
  vy: number;
}

export const InteractionGraph: React.FC<InteractionGraphProps> = ({
  drugs,
  height = 420,
  className = "",
}) => {
  const [graphData, setGraphData] = useState<GraphResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [nodePositions, setNodePositions] = useState<Record<string, NodePosition>>({});

  const containerRef = useRef<HTMLDivElement>(null);
  const isDraggingRef = useRef(false);
  const dragStartRef = useRef({ x: 0, y: 0 });

  useEffect(() => {
    let isMounted = true;
    const fetchGraph = async () => {
      if (!drugs || drugs.length < 2) {
        setIsLoading(false);
        setGraphData(null);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const data = await api.getGraph(drugs);
        if (isMounted) {
          setGraphData(data);

          // Calculate deterministic circular orbital positions for nodes
          const positions: Record<string, NodePosition> = {};
          const brandNodes = data.nodes.filter((n) => n.type === "Drug");
          const ingNodes = data.nodes.filter((n) => n.type === "Ingredient");

          const centerX = 300;
          const centerY = 200;

          // Outer ring for brand drugs
          const brandRadius = 140;
          brandNodes.forEach((node, i) => {
            const angle = (2 * Math.PI * i) / (brandNodes.length || 1);
            positions[node.id] = {
              x: centerX + brandRadius * Math.cos(angle),
              y: centerY + brandRadius * Math.sin(angle),
              vx: 0,
              vy: 0,
            };
          });

          // Inner ring for generic ingredients
          const ingRadius = 70;
          ingNodes.forEach((node, i) => {
            const angle = (2 * Math.PI * i) / (ingNodes.length || 1) + Math.PI / 6;
            positions[node.id] = {
              x: centerX + ingRadius * Math.cos(angle),
              y: centerY + ingRadius * Math.sin(angle),
              vx: 0,
              vy: 0,
            };
          });

          setNodePositions(positions);
          setIsLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError("Unable to load graph topology from knowledge base.");
          setIsLoading(false);
        }
      }
    };

    fetchGraph();

    return () => {
      isMounted = false;
    };
  }, [drugs]);

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

  if (isLoading) {
    return (
      <Card className={`p-8 text-center flex flex-col items-center justify-center bg-white ${className}`}>
        <Loader2 className="w-8 h-8 text-sky-600 animate-spin mb-2" />
        <p className="text-xs font-semibold text-slate-700">Constructing Graph Topology...</p>
        <p className="text-[11px] text-slate-400 mt-0.5">Fetching brand containment and interaction links</p>
      </Card>
    );
  }

  if (error || !graphData || graphData.nodes.length === 0) {
    return (
      <Card className={`p-6 text-center bg-white ${className}`}>
        <AlertCircle className="w-6 h-6 text-slate-400 mx-auto mb-2" />
        <p className="text-xs font-semibold text-slate-700">Graph Unavailable</p>
        <p className="text-[11px] text-slate-400 mt-1">{error || "Add at least 2 drugs to render graph."}</p>
      </Card>
    );
  }

  return (
    <Card className={`p-0 overflow-hidden bg-white border-slate-200 text-left ${className}`}>
      {/* Graph Toolbar */}
      <div className="px-4 py-3 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <GitGraph className="w-4 h-4 text-sky-600" />
          <h3 className="text-xs sm:text-sm font-bold text-slate-900">
            Interactive Subgraph Topology ({graphData.nodes.length} Nodes, {graphData.edges.length} Edges)
          </h3>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-1">
          <button
            onClick={handleZoomIn}
            className="p-1 rounded text-slate-500 hover:text-slate-800 hover:bg-slate-200 transition-colors cursor-pointer"
            title="Zoom In"
            aria-label="Zoom in"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-1 rounded text-slate-500 hover:text-slate-800 hover:bg-slate-200 transition-colors cursor-pointer"
            title="Zoom Out"
            aria-label="Zoom out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={handleResetView}
            className="p-1 rounded text-slate-500 hover:text-slate-800 hover:bg-slate-200 transition-colors cursor-pointer"
            title="Reset View"
            aria-label="Reset graph view"
          >
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* SVG Canvas */}
      <div
        ref={containerRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ height: typeof height === "number" ? `${height}px` : height }}
        className="w-full bg-slate-50/40 relative cursor-grab active:cursor-grabbing select-none overflow-hidden"
      >
        <svg
          width="100%"
          height="100%"
          viewBox="0 0 600 400"
          className="w-full h-full"
        >
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
                  {/* Midpoint Label */}
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
              const radius = isDrug ? 16 : 13;
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
                  {/* Outer ring on selection */}
                  {isSelected && (
                    <circle
                      cx={pos.x}
                      cy={pos.y}
                      r={radius + 4}
                      fill="none"
                      stroke="#0284C7"
                      strokeWidth="2"
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

                  {/* Node Label Text */}
                  <text
                    x={pos.x}
                    y={pos.y + radius + 12}
                    textAnchor="middle"
                    fill="#0F172A"
                    fontSize="10"
                    fontWeight="600"
                    className="select-none bg-white px-1 font-sans"
                  >
                    {node.label}
                  </text>
                </g>
              );
            })}
          </g>
        </svg>

        {/* Selected Node Details Drawer */}
        {selectedNode && (
          <div className="absolute top-3 left-3 bg-white p-3 rounded-lg border border-slate-200 shadow-md max-w-xs text-xs space-y-1">
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-900">{selectedNode.label}</span>
              <span
                className={`text-[10px] font-semibold px-1.5 py-0.5 rounded ${
                  selectedNode.type === "Drug"
                    ? "bg-sky-100 text-sky-800"
                    : "bg-emerald-100 text-emerald-800"
                }`}
              >
                {selectedNode.type === "Drug" ? "Brand Formulation" : "Active Generic"}
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-mono">ID: {selectedNode.id}</p>
          </div>
        )}
      </div>

      {/* Legend Footer */}
      <div className="px-4 py-2.5 bg-slate-50 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3 text-[11px] text-slate-600">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-600" />
            <span>Brand Drug</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-600" />
            <span>Active Ingredient</span>
          </span>
        </div>

        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-red-600" />
            <span>Major DDI</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-amber-500" />
            <span>Moderate DDI</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 border-t border-dashed border-purple-600" />
            <span>AI Predicted</span>
          </span>
        </div>
      </div>
    </Card>
  );
};
