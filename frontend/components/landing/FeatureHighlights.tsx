import React from "react";
import { BookOpen, Search, Shield, Zap, Globe, Lock } from "lucide-react";

const FEATURES = [
  {
    icon: BookOpen,
    label: "Citation-Backed Answers",
    description: "Every response includes exact page numbers and clause references from your document.",
  },
  {
    icon: Search,
    label: "Dual-Source RAG",
    description: "Answers are grounded in your document AND a curated Indian legal knowledge base.",
  },
  {
    icon: Shield,
    label: "Confidence Scoring",
    description: "Know how certain the AI is — high, medium, low, or not found in document.",
  },
  {
    icon: Zap,
    label: "Instant Processing",
    description: "Documents are processed, chunked, and embedded in under 30 seconds.",
  },
  {
    icon: Globe,
    label: "Indian Law Context",
    description: "Pre-seeded knowledge base covering Rental, Employment, Property, and Contract law.",
  },
  {
    icon: Lock,
    label: "Privacy First",
    description: "Documents are processed locally. Nothing is sent to third-party storage.",
  },
];

export default function FeatureHighlights() {
  return (
    <section id="features" className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-center text-text-primary text-3xl font-bold mb-3">
          Built for Indian Citizens
        </h2>
        <p className="text-center text-text-secondary mb-14">
          Features designed for legal clarity and document trust
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {FEATURES.map(({ icon: Icon, label, description }) => (
            <div
              key={label}
              className="bg-bg-surface border border-border-default hover:border-border-hover rounded-2xl p-6 transition-all duration-200 group hover:bg-bg-elevated"
            >
              <div className="w-11 h-11 rounded-xl bg-[rgba(34,197,94,0.10)] flex items-center justify-center mb-4">
                <Icon size={22} className="text-accent" />
              </div>
              <p className="text-text-primary font-semibold text-[15px] mb-2">{label}</p>
              <p className="text-text-secondary text-[13px] leading-relaxed">{description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
