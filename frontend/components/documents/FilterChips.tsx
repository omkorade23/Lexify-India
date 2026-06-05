"use client";

import React from "react";
import { cn } from "@/lib/utils";

import type { FilterOption } from "@/hooks/useDocuments";

interface FilterChipsProps {
  filters: readonly string[];
  active: string;
  onSelect: (f: FilterOption) => void;
}

export default function FilterChips({ filters, active, onSelect }: FilterChipsProps) {
  return (
    <div className="flex items-center gap-2 flex-wrap" role="group" aria-label="Filter documents">
      {filters.map((f) => (
        <button
          key={f}
          onClick={() => onSelect(f as FilterOption)}
          aria-pressed={f === active}
          className={cn(
            "px-3 py-1.5 rounded-full text-[12px] font-medium border transition-all duration-150",
            f === active
              ? "bg-[rgba(34,197,94,0.12)] border-[rgba(34,197,94,0.25)] text-accent"
              : "bg-white/[0.04] border-border-default text-text-secondary hover:bg-white/[0.06] hover:text-text-body"
          )}
        >
          {f}
        </button>
      ))}
    </div>
  );
}
