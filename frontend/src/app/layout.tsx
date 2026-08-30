import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { ToastProvider } from "@/components/feedback/Toast";
import { AnalysisProvider } from "@/context/AnalysisContext";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "PharmaSafe-KG — Explainable DDI Knowledge Graph & GNN System",
  description:
    "Explainable Knowledge Graph and Inductive Graph Neural Network (GraphSAGE) system for Drug-Drug Interaction detection, Indian brand-to-generic drug resolution, and polypharmacy analysis.",
  keywords: [
    "PharmaSafe-KG",
    "Drug-Drug Interactions",
    "Knowledge Graph",
    "Neo4j",
    "Graph Neural Network",
    "GraphSAGE",
    "Indian Medicine Resolver",
    "Polypharmacy",
  ],
  authors: [{ name: "PharmaSafe-KG Research Team" }],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full bg-slate-50">
      <body className={`${inter.className} min-h-full flex flex-col antialiased bg-slate-50 text-slate-900`}>
        <ToastProvider>
          <AnalysisProvider>
            <Navbar />
            <main className="flex-1 w-full">{children}</main>
            <Footer />
          </AnalysisProvider>
        </ToastProvider>
      </body>
    </html>
  );
}
