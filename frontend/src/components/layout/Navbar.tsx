"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  Menu,
  X,
  Presentation,
  FlaskConical,
  BookOpen,
  Home,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";
import { api } from "@/lib/api";
import { HealthResponse } from "@/types/api";

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
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

  const navLinks = [
    { href: "/", label: "Home", icon: <Home className="w-4 h-4" /> },
    { href: "/analyze", label: "Analyze DDI", icon: <FlaskConical className="w-4 h-4" /> },
    {
      href: "/demo",
      label: "Defense Demo",
      icon: <Presentation className="w-4 h-4" />,
      isSpecial: true,
    },
    { href: "/about", label: "Methodology", icon: <BookOpen className="w-4 h-4" /> },
  ];

  return (
    <header className="sticky top-0 z-40 w-full bg-white/95 backdrop-blur-xs border-b border-slate-200 shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand / Logo */}
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="flex items-center gap-2.5 group focus-visible:outline-2 focus-visible:outline-sky-600 rounded-md py-1"
            >
              <div className="w-9 h-9 rounded-lg bg-sky-600 flex items-center justify-center text-white shadow-xs group-hover:bg-sky-700 transition-colors">
                <Activity className="w-5 h-5" />
              </div>
              <div className="flex flex-col text-left">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-base text-slate-900 tracking-tight">
                    PharmaSafe-KG
                  </span>
                  <span className="bg-sky-50 text-sky-700 text-[10px] font-semibold px-1.5 py-0.5 rounded border border-sky-200">
                    v1.0
                  </span>
                </div>
                <span className="text-[11px] text-slate-500 font-medium hidden sm:inline-block">
                  Explainable DDI Knowledge Graph
                </span>
              </div>
            </Link>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-1" aria-label="Main Navigation">
            {navLinks.map((link) => {
              const isActive = pathname === link.href;

              if (link.isSpecial) {
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold uppercase tracking-wider transition-all select-none ${
                      isActive
                        ? "bg-indigo-600 text-white shadow-xs"
                        : "bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200"
                    }`}
                  >
                    {link.icon}
                    <span>{link.label}</span>
                  </Link>
                );
              }

              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors select-none ${
                    isActive
                      ? "text-sky-700 bg-sky-50 font-semibold"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                  }`}
                >
                  {link.icon}
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Live System Health Indicator */}
          <div className="hidden lg:flex items-center">
            {isHealthLoading ? (
              <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-50 px-2.5 py-1 rounded-full border border-slate-200">
                <span className="w-2 h-2 rounded-full bg-slate-300 animate-pulse" />
                <span>Checking API...</span>
              </div>
            ) : health?.status === "ok" ? (
              <div
                className="flex items-center gap-2 text-xs text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200 shadow-2xs"
                title={`Neo4j: ${health.neo4j} | GNN: ${health.gnn_loaded ? "Loaded" : "Fallback"} | Brands: ${health.brands_loaded.toLocaleString()}`}
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span className="font-semibold">KG & GNN Online</span>
              </div>
            ) : (
              <div
                className="flex items-center gap-2 text-xs text-amber-800 bg-amber-50 px-2.5 py-1 rounded-full border border-amber-200 shadow-2xs"
                title="FastAPI backend is offline or unreachable on http://localhost:8000"
              >
                <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                <span className="font-semibold">Backend Offline</span>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden items-center">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 rounded-md text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors focus-visible:outline-sky-600"
              aria-label="Toggle mobile navigation menu"
              aria-expanded={isMobileMenuOpen}
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 bg-white px-4 pt-2 pb-4 space-y-1 shadow-lg">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setIsMobileMenuOpen(false)}
                className={`flex items-center gap-2 px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-sky-50 text-sky-700 font-semibold"
                    : link.isSpecial
                    ? "bg-indigo-50 text-indigo-700 font-semibold border border-indigo-200"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                }`}
              >
                {link.icon}
                <span>{link.label}</span>
              </Link>
            );
          })}
        </div>
      )}
    </header>
  );
};
