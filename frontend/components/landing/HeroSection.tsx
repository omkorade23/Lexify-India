import React from "react";
import Link from "next/link";
import { ArrowRight, Shield, Zap, Lock } from "lucide-react";

const TRUST_SIGNALS = [
  { icon: Shield, label: "100% Private" },
  { icon: Zap, label: "Instant Analysis" },
  { icon: Lock, label: "No Data Stored" },
];

export default function HeroSection() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center px-6 pt-24 pb-20 overflow-hidden">
      {/* Atmospheric glow */}
      <div className="absolute inset-0 hero-glow pointer-events-none" aria-hidden="true" />

      {/* Badge */}
      <div className="relative mb-6 animate-fade-in">
        <span
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-[13px] font-medium text-accent border border-[rgba(34,197,94,0.25)] glass-medium"
          style={{ background: "rgba(34,197,94,0.12)" }}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
          AI-Powered Legal Intelligence
        </span>
      </div>

      {/* Headline */}
      <h1
        className="relative text-center text-4xl sm:text-5xl md:text-6xl font-bold text-text-primary leading-[1.1] tracking-tight max-w-3xl mb-6 animate-fade-in"
        style={{ animationDelay: "0.1s" }}
      >
        Your{" "}
        <span className="text-accent">AI Legal Assistant</span>
        <br />
        for India
      </h1>

      {/* Subheadline */}
      <p
        className="relative text-center text-text-secondary text-lg max-w-xl mb-10 leading-relaxed animate-fade-in"
        style={{ animationDelay: "0.2s" }}
      >
        Ask any legal question and get grounded answers. Upload a document for
        clause-by-clause analysis. No jargon, no confusion.
      </p>

      {/* CTAs */}
      <div
        className="relative flex flex-col sm:flex-row items-center gap-4 mb-12 animate-fade-in"
        style={{ animationDelay: "0.3s" }}
      >
        {/* Primary CTA → /chat */}
        <Link
          href="/chat"
          className="flex items-center gap-2.5 bg-accent hover:bg-accent-hover text-[#0A0A0A] font-semibold px-6 py-3 rounded-xl transition-all duration-200 hover:shadow-accent-glow"
          aria-label="Ask a legal question"
        >
          Ask a Legal Question
          <ArrowRight size={16} />
        </Link>

        {/* Secondary CTA → /documents */}
        <Link
          href="/documents"
          className="flex items-center gap-2 px-6 py-3 rounded-xl text-text-body border border-border-hover font-medium text-sm transition-all duration-200 hover:bg-white/[0.04]"
          style={{ background: "rgba(255,255,255,0.06)" }}
          aria-label="View my documents"
        >
          My Documents
        </Link>
      </div>

      {/* Trust signals */}
      <div
        className="relative flex flex-wrap items-center justify-center gap-6 animate-fade-in"
        style={{ animationDelay: "0.4s" }}
      >
        {TRUST_SIGNALS.map(({ icon: Icon, label }) => (
          <div key={label} className="flex items-center gap-2 text-text-muted text-[13px]">
            <Icon size={14} />
            <span>{label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
