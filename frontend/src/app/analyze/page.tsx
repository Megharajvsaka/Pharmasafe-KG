"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

export default function AnalyzePage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/dashboard?tab=analyse");
  }, [router]);

  return (
    <div className="w-full min-h-[60vh] flex items-center justify-center">
      <div className="flex items-center gap-2 text-sm text-slate-500">
        <Loader2 className="w-5 h-5 animate-spin text-sky-600" />
        <span>Redirecting to medication workbench...</span>
      </div>
    </div>
  );
}
