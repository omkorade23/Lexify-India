"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface ToggleRowProps {
  label: string;
  description?: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}

export default function ToggleRow({ label, description, checked, onChange }: ToggleRowProps) {
  const id = `toggle-${label.toLowerCase().replace(/\s+/g, "-")}`;

  return (
    <div className="flex items-center justify-between gap-4 py-4 border-b border-border-default last:border-b-0">
      <div className="flex-1 min-w-0">
        <label htmlFor={id} className="text-text-primary text-[13px] font-medium cursor-pointer">
          {label}
        </label>
        {description && (
          <p className="text-text-muted text-[12px] mt-0.5">{description}</p>
        )}
      </div>

      {/* Toggle switch */}
      <button
        id={id}
        role="switch"
        aria-checked={checked}
        aria-label={label}
        onClick={() => onChange(!checked)}
        className={cn(
          "relative inline-flex w-11 h-6 rounded-full transition-colors duration-200 shrink-0 focus-visible:outline-accent",
          checked ? "bg-accent" : "bg-white/[0.12]"
        )}
      >
        <span
          className={cn(
            "absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform duration-200",
            checked ? "translate-x-5" : "translate-x-0"
          )}
        />
      </button>
    </div>
  );
}
