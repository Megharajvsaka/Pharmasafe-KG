"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Activity, CheckCircle2, AlertTriangle, User, ShieldCheck } from "lucide-react";
import { api } from "@/lib/api";
import { HealthResponse } from "@/types/api";
import { useAuth } from "@/context/AuthContext";

export const Navbar: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isHealthLoading, setIsHealthLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const checkHealth = async () => {
      try {
        const data = await api.getHealth();
        if (isMounted) {
          setHealth(data);
          setIsHealthLoading(false);
        }
      } catch {
        if (isMounted) {
          setHealth(null);
          setIsHealthLoading(false);
        }
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="sticky top-0 z-40 w-full bg-white/95 backdrop-blur-xs border-b border-slate-200 shadow-2xs">
      <div className="w-full px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-18">
          {/* Brand / Logo (Enlarged & Prominent) */}
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="flex items-center gap-3 group focus-visible:outline-2 focus-visible:outline-sky-600 rounded-lg py-1.5"
            >
              <div className="w-11 h-11 rounded-xl bg-sky-600 flex items-center justify-center text-white shadow-sm group-hover:bg-sky-700 transition-colors">
                <Activity className="w-6 h-6" />
              </div>
              <div className="flex flex-col text-left">
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-xl sm:text-2xl text-slate-900 tracking-tight">
                    PharmaSafe-KG
                  </span>
                  <span className="bg-sky-50 text-sky-700 text-[10px] font-semibold px-1.5 py-0.5 rounded border border-sky-200">
                    v1.0
                  </span>
                </div>
                <span className="text-xs text-slate-500 font-medium">
                  Explainable Drug-Drug Interaction Knowledge Graph
                </span>
              </div>
            </Link>
          </div>

          {/* Right Area: Health Indicator & Auth Controls */}
          <div className="flex items-center gap-2.5 sm:gap-3.5">
            {/* Live System Health Indicator */}
            {isHealthLoading ? (
              <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-400 bg-slate-50 px-2.5 py-1 rounded-full border border-slate-200">
                <span className="w-2 h-2 rounded-full bg-slate-300 animate-pulse" />
                <span>Checking API...</span>
              </div>
            ) : health?.status === "ok" ? (
              <div
                className="flex items-center gap-1.5 text-xs text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200 shadow-2xs"
                title={`Neo4j: ${health.neo4j} | GNN: ${health.gnn_loaded ? "Loaded" : "Fallback"} | Brands: ${health.brands_loaded.toLocaleString()}`}
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span className="font-semibold hidden xs:inline">KG & GNN Online</span>
                <span className="font-semibold xs:hidden">Online</span>
              </div>
            ) : (
              <div
                className="flex items-center gap-1.5 text-xs text-amber-800 bg-amber-50 px-2.5 py-1 rounded-full border border-amber-200 shadow-2xs"
                title="FastAPI backend is offline or unreachable on http://localhost:8000"
              >
                <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                <span className="font-semibold">Backend Offline</span>
              </div>
            )}

            {/* Admin Demo Shortcut (for admins) */}
            {isAuthenticated && user?.role === "admin" && (
              <Link
                href="/admin?tab=demo"
                className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-50 hover:bg-purple-100 border border-purple-200 text-xs font-semibold text-purple-800 transition-colors"
              >
                <ShieldCheck className="w-3.5 h-3.5 text-purple-600" />
                <span>Admin Demo</span>
              </Link>
            )}

            {/* Authentication / Dashboard Button */}
            {isAuthenticated ? (
              <Link
                href={user?.role === "admin" ? "/admin" : "/dashboard"}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 border border-slate-200 text-xs text-slate-800 font-semibold transition-colors"
                title={user?.role === "admin" ? "Open Admin Dashboard" : `Logged in as ${user?.name}`}
              >
                <span
                  className={`w-6 h-6 rounded-full ${
                    user?.role === "admin" ? "bg-rose-600" : "bg-sky-600"
                  } text-white flex items-center justify-center text-xs font-bold`}
                >
                  {user?.avatarInitials}
                </span>
                <span className="max-w-[120px] truncate hidden sm:inline">{user?.name.split(" ")[0]}</span>
                <span className="text-[11px] font-normal text-slate-500 hidden md:inline">
                  {user?.role === "admin" ? "Admin Dashboard" : "Dashboard"}
                </span>
              </Link>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  href="/auth/login"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 transition-colors"
                >
                  <User className="w-3.5 h-3.5 text-slate-500" />
                  <span>Sign In</span>
                </Link>
                <Link
                  href="/auth/register"
                  className="flex items-center px-3.5 py-1.5 rounded-lg text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 shadow-xs transition-colors"
                >
                  <span>Register</span>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
