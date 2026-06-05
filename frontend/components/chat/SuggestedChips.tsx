"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface SuggestedChipsProps {
  chips: string[];
  onSelect: (chip: string) => void;
  className?: string;
}

export default function SuggestedChips({
  chips,
  onSelect,
  className,
}: SuggestedChipsProps) {
  if (!chips || chips.length === 0) return null;

  return (
    /*
     * Indent matches AI avatar (w-9 = 36px) + gap-3 (12px) = 48px
     * so chips align with the start of AI response text.
     * mt-4 above, mb-2 below, chips are width: fit-content and wrap.
     */
    <div
      className={cn("flex flex-wrap gap-2", className)}
      role="list"
      aria-label="Suggested questions"
      style={{ marginLeft: "48px", marginTop: "16px", marginBottom: "8px" }}
    >
      {chips.map((chip) => (
        <button
          key={chip}
          onClick={() => onSelect(chip)}
          role="listitem"
          className="px-3 py-1.5 rounded-full text-[13px] text-text-secondary border border-white/[0.08] bg-white/[0.04] hover:bg-[rgba(34,197,94,0.08)] hover:border-[rgba(34,197,94,0.20)] hover:text-text-body transition-all duration-200"
          style={{ width: "fit-content" }}
          aria-label={`Ask: ${chip}`}
        >
          {chip}
        </button>
      ))}
    </div>
  );
}
