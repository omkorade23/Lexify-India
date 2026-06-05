import React from "react";

// ProcessingTimeline is embedded inside ProcessingCard.
// This stub re-exports the visual steps for standalone use.

interface ProcessingTimelineProps {
  progress: number;
}

const STEPS = [
  { label: "Upload Received", threshold: 0 },
  { label: "OCR Extraction", threshold: 25 },
  { label: "Chunk & Embed", threshold: 55 },
  { label: "Analysis Ready", threshold: 90 },
];

export default function ProcessingTimeline({ progress }: ProcessingTimelineProps) {
  return (
    <ol className="space-y-3" aria-label="Processing steps">
      {STEPS.map((step, i) => {
        const done = progress > step.threshold + 20;
        const active = !done && progress >= step.threshold;
        return (
          <li key={step.label} className="flex items-center gap-3">
            <div className="shrink-0">
              {done ? (
                <div className="w-4 h-4 rounded-full bg-accent" aria-hidden="true" />
              ) : active ? (
                <div className="w-4 h-4 rounded-full border-2 border-accent border-t-transparent animate-spin" aria-hidden="true" />
              ) : (
                <div className="w-4 h-4 rounded-full bg-white/[0.12]" aria-hidden="true" />
              )}
            </div>
            <span
              className={
                done || active
                  ? "text-text-primary text-[13px]"
                  : "text-text-muted text-[13px]"
              }
            >
              {step.label}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
