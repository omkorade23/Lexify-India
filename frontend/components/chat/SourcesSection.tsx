import React from "react";
import type { Citation } from "@/lib/types";
import CitationCard from "./CitationCard";

interface SourcesSectionProps {
  citations: Citation[];
}

export default function SourcesSection({ citations }: SourcesSectionProps) {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-3">
      <p className="text-[11px] font-semibold uppercase tracking-[0.07em] text-text-placeholder mb-3">
        Sources Referenced
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {citations.map((c) => (
          <CitationCard key={c.chunk_id} citation={c} />
        ))}
      </div>
    </div>
  );
}
