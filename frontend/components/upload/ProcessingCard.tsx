import React from "react";
import { Sparkles } from "lucide-react";

interface ProcessingCardProps {
  filename: string;
  progress: number;
}

const TIMELINE_STEPS = [
  {
    label: "Document Received",
    description: "File uploaded successfully",
    threshold: 0,
  },
  {
    label: "Text Extraction",
    description: "Reading document contents with OCR",
    threshold: 30,
  },
  {
    label: "Embedding Generation",
    description: "Creating semantic vectors",
    threshold: 60,
  },
  {
    label: "Analysis Complete",
    description: "Document ready for queries",
    threshold: 95,
  },
];

export default function ProcessingCard({
  filename,
  progress,
}: ProcessingCardProps) {
  return (
    <div
      className="glass-strong bg-[rgba(18,22,18,0.80)] border border-white/[0.08] rounded-2xl p-8 max-w-md w-full mx-auto"
      role="status"
      aria-live="polite"
      aria-label={`Processing ${filename}, ${progress}% complete`}
    >
      {/* Icon */}
      <div className="flex justify-center mb-6">
        <div
          className="w-16 h-16 rounded-2xl bg-[rgba(34,197,94,0.15)] border border-[rgba(34,197,94,0.25)] flex items-center justify-center"
          style={{ boxShadow: "0 0 24px rgba(34, 197, 94, 0.30)" }}
        >
          <Sparkles size={28} className="text-accent" />
        </div>
      </div>

      <h2 className="text-text-primary text-lg font-semibold text-center mb-1">
        Processing your document...
      </h2>
      <p className="text-text-secondary text-sm text-center mb-6 truncate">
        {filename}
      </p>

      {/* Progress bar */}
      <div className="mb-2">
        <div className="h-1.5 rounded-full bg-white/[0.08] overflow-hidden">
          <div
            className="h-full bg-accent rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="flex items-center justify-between mt-1.5">
          <span className="text-[11px] text-text-muted">Initiated</span>
          <span className="text-[11px] text-text-muted font-medium">
            {progress}%
          </span>
          <span className="text-[11px] text-text-muted">Analysis</span>
        </div>
      </div>

      {/* Timeline */}
      <div className="mt-6 space-y-3">
        {TIMELINE_STEPS.map((step, i) => {
          const completed = progress > step.threshold + 20;
          const active =
            progress >= step.threshold && !completed && i > 0
              ? true
              : i === 0 && progress > 0;

          return (
            <div key={step.label} className="flex items-center gap-3">
              {/* Step indicator */}
              <div className="shrink-0">
                {completed ? (
                  <div className="w-5 h-5 rounded-full bg-accent flex items-center justify-center">
                    <svg
                      className="w-3 h-3 text-[#0A0A0A]"
                      fill="none"
                      viewBox="0 0 12 12"
                    >
                      <path
                        d="M2 6l3 3 5-5"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </div>
                ) : active ? (
                  <div className="w-5 h-5 rounded-full border-2 border-accent border-t-transparent animate-spin" />
                ) : (
                  <div className="w-5 h-5 rounded-full bg-white/[0.12]" />
                )}
              </div>

              {/* Labels */}
              <div>
                <p
                  className={
                    completed || active
                      ? "text-text-primary text-[13px] font-medium"
                      : "text-text-muted text-[13px]"
                  }
                >
                  {step.label}
                </p>
                <p
                  className={
                    active
                      ? "text-text-secondary text-[11px]"
                      : "text-text-muted text-[11px]"
                  }
                >
                  {step.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      <p className="text-center text-[11px] text-text-muted mt-6">
        This usually takes 15–30 seconds
      </p>
    </div>
  );
}
