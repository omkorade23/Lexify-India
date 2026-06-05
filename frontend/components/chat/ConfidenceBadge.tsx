import React from "react";
import { cn } from "@/lib/utils";
import type { QueryResponse } from "@/lib/types";

interface ConfidenceBadgeProps {
  confidence: QueryResponse["confidence"];
  className?: string;
}

const CONFIG: Record<
  QueryResponse["confidence"],
  { label: string; dotColor: string }
> = {
  high: { label: "High Confidence", dotColor: "bg-confidence-high" },
  medium: { label: "Medium Confidence", dotColor: "bg-confidence-medium" },
  low: { label: "Low Confidence", dotColor: "bg-confidence-low" },
  none: { label: "Not Found", dotColor: "bg-confidence-none" },
};

export default function ConfidenceBadge({
  confidence,
  className,
}: ConfidenceBadgeProps) {
  const { label, dotColor } = CONFIG[confidence];

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-white/[0.06] border border-white/[0.08] text-text-secondary",
        className
      )}
      role="status"
      aria-label={`Confidence: ${label}`}
    >
      <span className={cn("w-1.5 h-1.5 rounded-full shrink-0", dotColor)} />
      {label}
    </span>
  );
}
