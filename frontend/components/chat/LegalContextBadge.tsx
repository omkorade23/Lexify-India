import React from "react";
import { BookOpen } from "lucide-react";
import { cn } from "@/lib/utils";

interface LegalContextBadgeProps {
  className?: string;
}

export default function LegalContextBadge({ className }: LegalContextBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium",
        "bg-[rgba(34,197,94,0.10)] border border-[rgba(34,197,94,0.20)] text-accent",
        className
      )}
      role="status"
      aria-label="Legal context used"
    >
      <BookOpen size={11} />
      Legal Reference Used
    </span>
  );
}
