import React from "react";
import { cn, getDocumentTypeLabel } from "@/lib/utils";

interface DocumentTypeBadgeProps {
  type: string;
  className?: string;
}

export default function DocumentTypeBadge({ type, className }: DocumentTypeBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex text-[10px] font-semibold uppercase tracking-[0.05em] px-2 py-0.5 rounded",
        "bg-[rgba(34,197,94,0.10)] text-accent border border-[rgba(34,197,94,0.15)]",
        className
      )}
    >
      {getDocumentTypeLabel(type)}
    </span>
  );
}
