import React from "react";
import { Upload, MessageSquare, BookOpen, CheckCircle2 } from "lucide-react";

const STEPS = [
  {
    number: "01",
    icon: Upload,
    label: "Upload Your Document",
    description: "Upload any PDF, JPG, or PNG. Our OCR engine extracts text and structure with high accuracy.",
  },
  {
    number: "02",
    icon: MessageSquare,
    label: "Ask Your Question",
    description: "Type your question in plain English. No legal jargon required.",
  },
  {
    number: "03",
    icon: BookOpen,
    label: "Get Cited Answers",
    description: "Receive grounded answers with exact page references and relevant Indian law citations.",
  },
  {
    number: "04",
    icon: CheckCircle2,
    label: "Understand Clearly",
    description: "Review sources, check confidence scores, and feel confident before signing anything.",
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-center text-text-primary text-3xl font-bold mb-3">
          How It Works
        </h2>
        <p className="text-center text-text-secondary mb-16">
          From upload to understanding in four simple steps
        </p>

        <div className="relative grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Connecting line */}
          <div
            className="hidden md:block absolute top-8 left-[12.5%] right-[12.5%] h-px bg-border-default"
            aria-hidden="true"
          />

          {STEPS.map((step, i) => (
            <div key={step.number} className="flex flex-col items-center text-center gap-4">
              {/* Step circle */}
              <div className="relative z-10 w-16 h-16 rounded-full bg-bg-base border-2 border-accent flex items-center justify-center">
                <span className="text-accent font-bold text-sm">{step.number}</span>
              </div>

              {/* Card */}
              <div className="bg-bg-surface border border-border-default rounded-2xl p-4 w-full">
                <div className="w-9 h-9 rounded-xl bg-[rgba(34,197,94,0.10)] flex items-center justify-center mx-auto mb-3">
                  <step.icon size={18} className="text-accent" />
                </div>
                <p className="text-text-primary font-semibold text-sm mb-2">{step.label}</p>
                <p className="text-text-secondary text-[12px] leading-relaxed">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
