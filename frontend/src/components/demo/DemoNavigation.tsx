"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  ArrowRight,
  RotateCcw,
  FlaskConical,
  Keyboard,
  ListTree,
} from "lucide-react";
import { Button } from "@/components/ui/Button";

export interface DemoNavigationProps {
  currentStepIndex: number;
  totalSteps: number;
  onNext: () => void;
  onPrev: () => void;
  onRestart: () => void;
  onToggleOverview?: () => void;
  isNextDisabled?: boolean;
  className?: string;
}

export const DemoNavigation: React.FC<DemoNavigationProps> = ({
  currentStepIndex,
  totalSteps,
  onNext,
  onPrev,
  onRestart,
  onToggleOverview,
  isNextDisabled = false,
  className = "",
}) => {
  const isFirstStep = currentStepIndex === 0;
  const isLastStep = currentStepIndex === totalSteps - 1;

  // Keyboard navigation handler
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if inside an input or textarea
      if (
        document.activeElement?.tagName === "INPUT" ||
        document.activeElement?.tagName === "TEXTAREA"
      ) {
        return;
      }

      if (e.key === "ArrowRight" && !isLastStep && !isNextDisabled) {
        e.preventDefault();
        onNext();
      } else if (e.key === "ArrowLeft" && !isFirstStep) {
        e.preventDefault();
        onPrev();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isFirstStep, isLastStep, isNextDisabled, onNext, onPrev]);

  return (
    <div
      className={`sticky bottom-0 z-30 w-full bg-white/95 backdrop-blur-xs border-t border-slate-200 py-3.5 px-4 sm:px-8 shadow-md ${className}`}
    >
      <div className="max-w-6xl mx-auto flex items-center justify-between gap-4 flex-wrap">
        {/* Left Side: Restart & Workbench Exit */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onRestart}
            leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
            title="Restart Presentation from Step 1"
          >
            Restart Demo
          </Button>

          <Link href="/analyze">
            <Button
              variant="ghost"
              size="sm"
              leftIcon={<FlaskConical className="w-3.5 h-3.5 text-sky-600" />}
              className="hidden sm:inline-flex text-slate-600"
            >
              Exit to Live Workbench
            </Button>
          </Link>
        </div>

        {/* Center: Keyboard hint */}
        <div className="hidden md:flex items-center gap-1.5 text-[11px] text-slate-400 font-mono select-none">
          <Keyboard className="w-3.5 h-3.5 text-slate-400" />
          <span>Use</span>
          <kbd className="px-1.5 py-0.5 bg-slate-100 border border-slate-200 rounded text-[10px]">
            ←
          </kbd>
          <kbd className="px-1.5 py-0.5 bg-slate-100 border border-slate-200 rounded text-[10px]">
            →
          </kbd>
          <span>keys to navigate</span>
        </div>

        {/* Right Side: Step Stepper Controls */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="md"
            onClick={onPrev}
            disabled={isFirstStep}
            leftIcon={<ArrowLeft className="w-4 h-4" />}
          >
            Previous
          </Button>

          {isLastStep ? (
            <Link href="/analyze">
              <Button
                variant="primary"
                size="md"
                rightIcon={<FlaskConical className="w-4 h-4" />}
                className="font-semibold shadow-xs"
              >
                Launch Workbench
              </Button>
            </Link>
          ) : (
            <Button
              variant="primary"
              size="md"
              onClick={onNext}
              disabled={isNextDisabled}
              rightIcon={<ArrowRight className="w-4 h-4" />}
              className="font-semibold shadow-xs"
            >
              Next Step
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};
