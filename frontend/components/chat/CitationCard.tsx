import React from "react";
import type { Citation } from "@/lib/types";
import { cn } from "@/lib/utils";

interface CitationCardProps {
  citation: Citation;
  className?: string;
}

export default function CitationCard({ citation, className }: CitationCardProps) {
  const isDocument = citation.source_type === "document";

  return (
    <div
      className={cn(
        "rounded-[10px] p-4 flex flex-col gap-2 glass-subtle",
        "bg-citation-surface border border-border-default",
        isDocument
          ? "border-l-[2px] border-l-accent"
          : "border-l-[2px] border-l-[rgba(34,197,94,0.40)]",
        className
      )}
    >
      {/* Header row */}
      <div className="flex items-center justify-between gap-2">
        <span
          className={cn(
            "text-[11px] font-semibold uppercase tracking-[0.07em]",
            isDocument ? "text-accent" : "text-[rgba(34,197,94,0.65)]"
          )}
        >
          {isDocument ? "Source Document" : "Legal Precedent Context"}
        </span>

        {isDocument && citation.page_number != null && (
          <span className="text-[11px] text-text-muted shrink-0">
            {citation.section ? `${citation.section} · ` : ""}
            Pg. {citation.page_number}
          </span>
        )}
        {!isDocument && citation.act_name && (
          <span className="text-[11px] text-text-muted shrink-0 text-right">
            {citation.act_section ?? citation.act_name}
          </span>
        )}
      </div>

      {/* Body */}
      <p
        className={cn(
          "text-[13px] leading-[1.7]",
          isDocument ? "italic text-text-body" : "text-text-secondary"
        )}
      >
        {isDocument ? `"${citation.text}"` : citation.text}
      </p>

      {/* Act name for legal reference */}
      {!isDocument && citation.act_name && (
        <p className="text-[11px] text-text-muted">{citation.act_name}</p>
      )}
    </div>
  );
}
