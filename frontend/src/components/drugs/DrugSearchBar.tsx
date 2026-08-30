"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { Search, Loader2, Plus, CornerDownLeft, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";

export interface DrugSearchBarProps {
  onSelectDrug: (drugName: string) => void;
  disabled?: boolean;
  maxReached?: boolean;
  className?: string;
}

export const DrugSearchBar: React.FC<DrugSearchBarProps> = ({
  onSelectDrug,
  disabled = false,
  maxReached = false,
  className = "",
}) => {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState<number>(-1);
  const [searchError, setSearchError] = useState<string | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Debounced autocomplete search (300ms)
  useEffect(() => {
    const trimmed = query.trim();
    if (trimmed.length < 2) {
      setSuggestions([]);
      setIsOpen(false);
      setIsLoading(false);
      setSearchError(null);
      return;
    }

    setIsLoading(true);
    setSearchError(null);

    const timer = setTimeout(async () => {
      try {
        const data = await api.searchBrands(trimmed, 10);
        setSuggestions(data.results || []);
        setIsOpen(true);
        setHighlightedIndex(-1);
      } catch {
        setSuggestions([]);
        setSearchError("Failed to fetch autocomplete suggestions.");
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  // Click outside listener
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = useCallback(
    (name: string) => {
      const clean = name.trim();
      if (clean) {
        onSelectDrug(clean);
        setQuery("");
        setSuggestions([]);
        setIsOpen(false);
        setHighlightedIndex(-1);
        inputRef.current?.focus();
      }
    },
    [onSelectDrug]
  );

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen || suggestions.length === 0) {
      if (e.key === "Enter" && query.trim()) {
        e.preventDefault();
        handleSelect(query);
      }
      return;
    }

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setHighlightedIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : 0));
        break;
      case "ArrowUp":
        e.preventDefault();
        setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : suggestions.length - 1));
        break;
      case "Enter":
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < suggestions.length) {
          handleSelect(suggestions[highlightedIndex]);
        } else if (query.trim()) {
          handleSelect(query);
        }
        break;
      case "Escape":
        e.preventDefault();
        setIsOpen(false);
        setHighlightedIndex(-1);
        break;
    }
  };

  return (
    <div ref={containerRef} className={`relative w-full ${className}`}>
      <div className="relative flex items-center">
        <div className="absolute left-3 text-slate-400 pointer-events-none flex items-center">
          <Search className="w-4 h-4" />
        </div>

        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => {
            if (query.trim().length >= 2 && suggestions.length > 0) {
              setIsOpen(true);
            }
          }}
          onKeyDown={handleKeyDown}
          disabled={disabled || maxReached}
          role="combobox"
          aria-autocomplete="list"
          aria-expanded={isOpen}
          aria-controls="drug-search-results"
          aria-activedescendant={
            highlightedIndex >= 0 ? `suggestion-item-${highlightedIndex}` : undefined
          }
          placeholder={
            maxReached
              ? "Maximum 10 medications reached."
              : "Search Indian brand or generic name (e.g. Combiflam, Ecosprin, Warfarin)..."
          }
          className="w-full bg-white text-slate-900 placeholder:text-slate-400 text-sm rounded-md border border-slate-300 pl-9 pr-24 py-2.5 shadow-2xs focus-visible:outline-2 focus-visible:outline-sky-600 hover:border-slate-400 transition-colors disabled:bg-slate-100 disabled:cursor-not-allowed"
        />

        <div className="absolute right-2 flex items-center gap-1.5">
          {isLoading && <Loader2 className="w-4 h-4 text-sky-600 animate-spin mr-1" />}

          {query.trim() && !disabled && !maxReached && (
            <button
              type="button"
              onClick={() => handleSelect(query)}
              className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold bg-sky-600 hover:bg-sky-700 text-white rounded transition-colors shadow-2xs cursor-pointer select-none"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add</span>
            </button>
          )}
        </div>
      </div>

      {/* Autocomplete Dropdown */}
      {isOpen && (
        <div
          id="drug-search-results"
          role="listbox"
          className="absolute z-50 left-0 right-0 mt-1.5 bg-white rounded-lg border border-slate-200 shadow-lg max-h-64 overflow-y-auto divide-y divide-slate-100 animate-in fade-in zoom-in-95 duration-100"
        >
          {suggestions.length > 0 ? (
            <>
              <div className="px-3 py-1.5 bg-slate-50 text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between">
                <span>Matching Formulations</span>
                <span className="flex items-center gap-1">
                  <CornerDownLeft className="w-3 h-3" /> Select
                </span>
              </div>
              {suggestions.map((suggestion, index) => {
                const isHighlighted = index === highlightedIndex;
                return (
                  <div
                    key={suggestion}
                    id={`suggestion-item-${index}`}
                    role="option"
                    aria-selected={isHighlighted}
                    onClick={() => handleSelect(suggestion)}
                    onMouseEnter={() => setHighlightedIndex(index)}
                    className={`px-3.5 py-2.5 text-xs sm:text-sm font-medium flex items-center justify-between cursor-pointer select-none transition-colors ${
                      isHighlighted
                        ? "bg-sky-50 text-sky-900 font-semibold"
                        : "text-slate-700 hover:bg-slate-50"
                    }`}
                  >
                    <span>{suggestion}</span>
                    <Plus className={`w-3.5 h-3.5 ${isHighlighted ? "text-sky-600" : "text-slate-300"}`} />
                  </div>
                );
              })}
            </>
          ) : query.trim().length >= 2 && !isLoading ? (
            <div className="p-4 text-center text-xs text-slate-500">
              <p className="font-medium text-slate-700">No catalog match found for &quot;{query}&quot;</p>
              <p className="mt-1 text-slate-400">
                Press <kbd className="px-1.5 py-0.5 bg-slate-100 border border-slate-200 rounded text-[10px] font-mono">Enter</kbd> or click <strong>Add</strong> to add as a custom drug name.
              </p>
            </div>
          ) : null}

          {searchError && (
            <div className="p-3 bg-red-50 text-xs text-red-700 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
              <span>{searchError}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
