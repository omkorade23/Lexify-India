"use client";

import React, { useEffect, useState } from "react";
import { Scale } from "lucide-react";
import { cn } from "@/lib/utils";

// Section IDs must match those set in app/page.tsx
const scrollTo = (id: string) => (e: React.MouseEvent) => {
  e.preventDefault();
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
};

const NAV_LINKS = [
  { id: "how-it-works", label: "How It Works" },
  { id: "document-types", label: "Document Types" },
  { id: "features", label: "Features" },
];

export default function LandingNav() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handler, { passive: true });
    return () => window.removeEventListener("scroll", handler);
  }, []);

  return (
    <header
      className={cn(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-300",
        scrolled ? "nav-scrolled" : "bg-transparent"
      )}
    >
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center gap-8">
        {/* Logo — smooth-scrolls to top on click */}
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          className="flex items-center gap-2.5 mr-auto md:mr-0 cursor-pointer"
          aria-label="Back to top"
          style={{ cursor: "pointer" }}
        >
          <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center">
            <Scale size={15} className="text-[#0A0A0A]" />
          </div>
          <span className="text-text-primary font-semibold text-[15px]">
            Lexify India
          </span>
        </button>

        {/* Center links — smooth-scroll to sections */}
        <nav className="hidden md:flex items-center gap-6 mx-auto" aria-label="Landing navigation">
          {NAV_LINKS.map(({ id, label }) => (
            <a
              key={id}
              href="javascript:void(0)"
              onClick={scrollTo(id)}
              className="text-text-secondary hover:text-text-body text-[14px] transition-colors cursor-pointer"
            >
              {label}
            </a>
          ))}
        </nav>

        {/* Right CTAs */}
        <div className="flex items-center gap-3 ml-auto md:ml-0">
          <a
            href="javascript:void(0)"
            onClick={(e) => {
              e.preventDefault();
              window.location.href = "/chat";
            }}
            className="hidden md:inline-flex text-text-secondary hover:text-text-body text-sm transition-colors cursor-pointer"
            aria-label="Log in"
          >
            Log In
          </a>
          <a
            href="/chat"
            className="inline-flex items-center gap-2 bg-accent hover:bg-accent-hover text-[#0A0A0A] text-sm font-semibold px-4 py-2 rounded-lg transition-all duration-200 hover:shadow-accent-glow-sm"
            aria-label="Get started"
          >
            Get Started
          </a>
        </div>
      </div>
    </header>
  );
}
