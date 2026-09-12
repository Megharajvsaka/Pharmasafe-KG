"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Activity, Mail, ArrowRight, ArrowLeft, AlertCircle, Info } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { AuthNotice } from "@/components/auth/AuthNotice";
import { useAuth } from "@/context/AuthContext";

export default function ForgotPasswordPage() {
  const { forgotPassword } = useAuth();
  const [email, setEmail] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setIsLoading(true);

    const res = await forgotPassword(email);
    setIsLoading(false);

    if (!res.success) {
      setErrorMessage(
        res.error ||
          "SMTP email service is not configured on this research server. Please contact your system administrator."
      );
    }
  };

  return (
    <div className="w-full min-h-[calc(100vh-140px)] flex items-center justify-center py-12 px-4 sm:px-6">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <Link href="/" className="inline-flex items-center gap-2 mb-2 group">
            <div className="w-10 h-10 rounded-xl bg-sky-600 flex items-center justify-center text-white shadow-xs group-hover:bg-sky-700 transition-colors">
              <Activity className="w-6 h-6" />
            </div>
            <span className="font-bold text-xl text-slate-900 tracking-tight">
              PharmaSafe-KG
            </span>
          </Link>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Reset Password
          </h1>
          <p className="text-xs sm:text-sm text-slate-500">
            Account recovery for registered institutional researchers.
          </p>
        </div>

        <Card className="p-6 sm:p-8 space-y-5 bg-white border-slate-200 shadow-sm text-left">
          <AuthNotice />

          {/* Infrastructure notice */}
          <div className="p-3 bg-amber-50 rounded-md border border-amber-200 text-xs text-amber-800 flex items-start gap-2">
            <Info className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <span>
              Automated email dispatch is not yet enabled on this research server. If you have
              forgotten your credentials, please register a new account or contact the system administrator.
            </span>
          </div>

          {errorMessage && (
            <div className="p-3 bg-red-50 rounded-md border border-red-200 text-xs text-red-700 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5"
              >
                Institutional Email
              </label>
              <div className="relative">
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@hospital.edu.in"
                  className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-md text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                />
                <Mail className="w-4 h-4 text-slate-400 absolute right-3.5 top-3 pointer-events-none" />
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="md"
              disabled={isLoading}
              className="w-full font-semibold shadow-xs"
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              {isLoading ? "Checking Server..." : "Request Password Reset"}
            </Button>
          </form>

          <div className="pt-4 border-t border-slate-100 text-center">
            <Link
              href="/auth/login"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Sign In</span>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
