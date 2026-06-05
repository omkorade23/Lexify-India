"use client";

import React from "react";

interface TypographySliderProps {
  value: number;
  onChange: (v: number) => void;
  min?: number;
  max?: number;
}

export default function TypographySlider({
  value,
  onChange,
  min = 12,
  max = 20,
}: TypographySliderProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-text-secondary text-sm">Font Size</span>
        <span className="text-text-primary text-sm font-semibold">{value}px</span>
      </div>

      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full"
        aria-label={`Font size: ${value} pixels`}
        aria-valuemin={min}
        aria-valuemax={max}
        aria-valuenow={value}
      />

      <div className="flex items-center justify-between text-[11px] text-text-muted">
        <span>Small ({min}px)</span>
        <span>Large ({max}px)</span>
      </div>

      {/* Preview */}
      <div
        className="bg-bg-sidebar border-l-[3px] border-l-[rgba(34,197,94,0.35)] rounded-xl px-4 py-3"
        aria-label="Typography preview"
      >
        <p
          className="italic text-text-body leading-relaxed"
          style={{ fontSize: `${value}px` }}
        >
          &quot;The lock-in period stipulated under Clause 4 shall be 36 months from the commencement date.&quot;
        </p>
      </div>
    </div>
  );
}
