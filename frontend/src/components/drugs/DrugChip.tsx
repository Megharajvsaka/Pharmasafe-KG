"use client";

import React from "react";
import Link from "next/link";
import { Pill, X, ExternalLink } from "lucide-react";
import { motion } from "framer-motion";

export interface DrugChipProps {
  name: string;
  onRemove: (name: string) => void;
  index?: number;
  disabled?: boolean;
  showMonographLink?: boolean;
}

export const DrugChip: React.FC<DrugChipProps> = ({
  name,
  onRemove,
  index = 0,
  disabled = false,
  showMonographLink = true,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 4 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.15, delay: index * 0.02 }}
      className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-sky-50 text-sky-900 border border-sky-200 rounded-md text-xs sm:text-sm font-medium shadow-2xs group hover:bg-sky-100/80 transition-colors select-none"
    >
      <Pill className="w-3.5 h-3.5 text-sky-600 shrink-0" />
      <span className="font-semibold">{name}</span>

      {showMonographLink && (
        <Link
          href={`/drugs/${encodeURIComponent(name)}`}
          target="_blank"
          className="text-sky-400 hover:text-sky-700 p-0.5 rounded transition-colors"
          title={`View ${name} monograph (opens in new tab)`}
          onClick={(e) => e.stopPropagation()}
        >
          <ExternalLink className="w-3 h-3" />
        </Link>
      )}

      {!disabled && (
        <button
          type="button"
          onClick={() => onRemove(name)}
          className="p-0.5 ml-0.5 rounded text-sky-400 hover:text-red-600 hover:bg-sky-200/60 transition-colors cursor-pointer focus-visible:outline-sky-600"
          aria-label={`Remove ${name}`}
          title={`Remove ${name}`}
        >
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </motion.div>
  );
};
