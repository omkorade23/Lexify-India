import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Backgrounds
        "bg-base": "#080C08",
        "bg-sidebar": "#1A1A1A",
        "bg-surface": "#252525",
        "bg-elevated": "#2A2A2A",
        "bg-hover": "#2E2E2E",
        "bg-input": "#0F1A0F",

        // Accent
        accent: "#22C55E",
        "accent-hover": "#16A34A",
        "accent-dim": "rgba(34, 197, 94, 0.12)",
        "accent-border": "rgba(34, 197, 94, 0.25)",
        "accent-glow": "rgba(34, 197, 94, 0.30)",

        // Text
        "text-primary": "#FFFFFF",
        "text-body": "#EFEFEF",
        "text-secondary": "#888888",
        "text-muted": "#666666",
        "text-placeholder": "#4A4A4A",

        // Borders
        "border-default": "rgba(255, 255, 255, 0.06)",
        "border-hover": "rgba(255, 255, 255, 0.10)",
        "border-active": "#22C55E",

        // Citation surfaces
        "citation-surface": "#0D1A0D",

        // Semantic
        "confidence-high": "#22C55E",
        "confidence-medium": "#F59E0B",
        "confidence-low": "#F97316",
        "confidence-none": "#666666",
        danger: "#EF4444",
        warning: "#F59E0B",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      fontSize: {
        "2xs": ["11px", { lineHeight: "1.4", letterSpacing: "0.07em" }],
      },
      borderRadius: {
        "4xl": "2rem",
      },
      backdropBlur: {
        xs: "4px",
        sm: "8px",
        xl: "20px",
      },
      boxShadow: {
        "accent-glow": "0 0 28px rgba(34, 197, 94, 0.35)",
        "accent-glow-sm": "0 0 16px rgba(34, 197, 94, 0.30)",
        "accent-glow-md": "0 0 24px rgba(34, 197, 94, 0.30)",
      },
      keyframes: {
        "fade-in": {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "spin-slow": {
          to: { transform: "rotate(360deg)" },
        },
        pulse: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.4" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.3s ease-out",
        "spin-slow": "spin-slow 1.5s linear infinite",
        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        shimmer: "shimmer 2s linear infinite",
      },
    },
  },
  plugins: [],
};

export default config;
