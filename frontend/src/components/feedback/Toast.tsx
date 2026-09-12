"use client";

import React, { createContext, useContext, useState, useCallback } from "react";
import { CheckCircle2, AlertCircle, Info, X } from "lucide-react";

export type ToastType = "success" | "error" | "info";

export interface ToastMessage {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
}

export interface ToastOptions {
  type?: ToastType;
  title: string;
  description?: string;
  message?: string;
}

interface ToastContextType {
  showToast: (
    typeOrOptions: ToastType | ToastOptions,
    title?: string,
    message?: string
  ) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
};

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const showToast = useCallback(
    (typeOrOptions: ToastType | ToastOptions, title?: string, message?: string) => {
      const id = Math.random().toString(36).substring(2, 9);

      let finalType: ToastType = "info";
      let finalTitle = "";
      let finalMessage: string | undefined = undefined;

      if (typeof typeOrOptions === "object") {
        finalType = typeOrOptions.type || "info";
        finalTitle = typeOrOptions.title || "";
        finalMessage = typeOrOptions.description || typeOrOptions.message;
      } else {
        finalType = typeOrOptions;
        finalTitle = title || "";
        finalMessage = message;
      }

      setToasts((prev) => [...prev, { id, type: finalType, title: finalTitle, message: finalMessage }]);

      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, 4000);
    },
    []
  );

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div
        className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none"
        aria-live="polite"
      >
        {toasts.map((t) => {
          const icons = {
            success: <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />,
            error: <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />,
            info: <Info className="w-4 h-4 text-sky-600 shrink-0 mt-0.5" />,
          };

          const borders = {
            success: "border-emerald-200 bg-white",
            error: "border-red-200 bg-white",
            info: "border-sky-200 bg-white",
          };

          return (
            <div
              key={t.id}
              className={`pointer-events-auto p-3.5 rounded-lg border shadow-lg flex items-start gap-2.5 transition-all ${borders[t.type]}`}
              role="alert"
            >
              {icons[t.type]}
              <div className="flex-1 text-left">
                <h5 className="text-xs font-semibold text-slate-900">{t.title}</h5>
                {t.message && <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">{t.message}</p>}
              </div>
              <button
                onClick={() => removeToast(t.id)}
                className="text-slate-400 hover:text-slate-600 p-0.5 rounded-sm cursor-pointer"
                aria-label="Dismiss toast"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
};
