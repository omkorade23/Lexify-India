"use client";


import Link from "next/link";
import { Scale } from "lucide-react";

const TRUST_BADGES = ["100% Private", "No Data Stored", "Indian Law Context"];

const PRODUCT_LINKS = [
  { href: "/chat", label: "Chat Workspace" },
  { href: "/documents", label: "My Documents" },
  { href: "/upload", label: "Upload Document" },
  { href: "/settings", label: "Settings" },
];

const BUILT_WITH = [
  "Next.js 16 (App Router)",
  "FastAPI (Python)",
  "Google Gemini 2.5 Flash",
  "ChromaDB Vector Store",
  "PaddleOCR",
  "Tailwind CSS v4",
];

const COL_HEADING = {
  fontSize: "13px",
  fontWeight: 600,
  color: "#ffffff",
  textTransform: "uppercase" as const,
  letterSpacing: "0.07em",
  marginBottom: "16px",
};

export default function Footer() {
  return (
    <footer
      style={{
        background: "#080C08",
        borderTop: "1px solid rgba(255,255,255,0.06)",
        padding: "64px 0 40px",
      }}
    >
      <div className="max-w-6xl mx-auto px-6">
        {/* ── Four-column grid ─────────────────────────────────────── */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "48px",
            marginBottom: "48px",
          }}
        >
          {/* Column 1 — About */}
          <div>
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center">
                <Scale size={15} className="text-[#0A0A0A]" />
              </div>
              <span
                style={{
                  color: "#ffffff",
                  fontWeight: 600,
                  fontSize: "15px",
                }}
              >
                Lexify India
              </span>
            </div>

            <p
              style={{
                color: "#888888",
                fontSize: "14px",
                lineHeight: 1.6,
                marginBottom: "16px",
                maxWidth: "280px",
              }}
            >
              AI-powered legal document intelligence for Indian citizens. Upload,
              analyze, and understand legal documents in plain language — before
              you sign.
            </p>

            {/* Trust badges */}
            <div className="flex flex-wrap gap-2">
              {TRUST_BADGES.map((badge) => (
                <span
                  key={badge}
                  style={{
                    background: "rgba(34,197,94,0.08)",
                    border: "1px solid rgba(34,197,94,0.20)",
                    color: "#22C55E",
                    fontSize: "11px",
                    borderRadius: "20px",
                    padding: "4px 10px",
                    fontWeight: 500,
                  }}
                >
                  {badge}
                </span>
              ))}
            </div>
          </div>

          {/* Column 2 — Product */}
          <div>
            <p style={COL_HEADING}>Product</p>
            <ul className="space-y-0">
              {PRODUCT_LINKS.map(({ href, label }) => (
                <li key={href}>
                  <Link
                    href={href}
                    style={{
                      color: "#888888",
                      fontSize: "14px",
                      lineHeight: 2,
                      display: "block",
                      transition: "color 0.15s",
                    }}
                    onMouseOver={(e) =>
                      ((e.target as HTMLElement).style.color = "#EFEFEF")
                    }
                    onMouseOut={(e) =>
                      ((e.target as HTMLElement).style.color = "#888888")
                    }
                  >
                    {label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Column 3 — Built With */}
          <div>
            <p style={COL_HEADING}>Built With</p>
            <ul className="space-y-0">
              {BUILT_WITH.map((item) => (
                <li
                  key={item}
                  style={{
                    color: "#888888",
                    fontSize: "14px",
                    lineHeight: 2,
                  }}
                >
                  {item}
                </li>
              ))}
            </ul>
          </div>

          {/* Column 4 — Developer */}
          <div>
            <p style={COL_HEADING}>Developer</p>
            <p
              style={{
                color: "#EFEFEF",
                fontSize: "14px",
                marginBottom: "4px",
              }}
            >
              Om Korade
            </p>
            <p
              style={{
                color: "#666666",
                fontSize: "13px",
                marginBottom: "12px",
              }}
            >
              Built for Indian legal accessibility.
            </p>
            <span
              style={{
                color: "#666666",
                fontSize: "13px",
              }}
            >
              Open Source · India
            </span>
          </div>
        </div>

        {/* ── Bottom bar ──────────────────────────────────────────── */}
        <div
          style={{
            borderTop: "1px solid rgba(255,255,255,0.06)",
            paddingTop: "24px",
            paddingBottom: "24px",
            display: "flex",
            flexWrap: "wrap",
            alignItems: "flex-start",
            justifyContent: "space-between",
            gap: "12px",
          }}
        >
          <p style={{ color: "#666666", fontSize: "13px" }}>
            © 2026 Lexify India. All rights reserved.
          </p>
          <p
            style={{
              color: "#666666",
              fontSize: "12px",
              maxWidth: "480px",
              textAlign: "right",
            }}
          >
            DISCLAIMER: Lexify India is an AI tool and does not provide legal
            advice. Always consult a qualified advocate for official legal
            counsel.
          </p>
        </div>
      </div>
    </footer>
  );
}
