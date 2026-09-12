"use client";

import React from "react";
import { ShieldCheck } from "lucide-react";

export const AuthNotice: React.FC<{ className?: string }> = ({ className = "" }) => {
  return (
    <div
      className={`p-3.5 bg-emerald-50/90 rounded-lg border border-emerald-200 text-xs text-emerald-900 leading-relaxed flex items-start gap-2.5 ${className}`}
    >
      <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
      <div>
        <strong className="font-semibold block mb-0.5">
          PostgreSQL Secure Authentication Active:
        </strong>
        <span>
          User credentials are encrypted via Argon2id password hashing. Sessions are managed through
          signed JWTs and rotating HttpOnly refresh cookies. Saved regimens and analysis history are
          persisted to PostgreSQL with strict account isolation.
        </span>
      </div>
    </div>
  );
};
