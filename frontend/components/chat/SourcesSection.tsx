"use client";

import React, { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import type { Citation } from "@/lib/types";

interface SourcesSectionProps {
  citations: Citation[];
}

export default function SourcesSection({ citations }: SourcesSectionProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [hovered, setHovered] = useState(false);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="w-full">
      <button
        onClick={() => setIsOpen(!isOpen)}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        style={{
          background: hovered ? "rgba(255,255,255,0.07)" : "rgba(255,255,255,0.04)",
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: "20px",
          padding: "6px 14px",
          fontSize: "13px",
          color: hovered ? "#EFEFEF" : "#888888",
          cursor: "pointer",
          marginTop: "12px",
          marginLeft: "48px",
          display: "inline-flex",
          alignItems: "center",
          gap: "6px",
          outline: "none",
          transition: "all 0.15s ease",
        }}
      >
        <span>{isOpen ? "Hide Sources" : `View Sources (${citations.length})`}</span>
        {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      {isOpen && (
        <div
          style={{
            marginTop: "8px",
            marginLeft: "48px",
            display: "flex",
            flexDirection: "column",
            gap: "4px",
          }}
        >
          {citations.map((c, index) => {
            const isDocument = c.source_type === "document";
            let label = "";
            if (isDocument) {
              if (c.page_number != null && c.section) {
                const sectionStr = c.section.toLowerCase().startsWith("clause") || c.section.toLowerCase().startsWith("section")
                  ? c.section
                  : `Clause ${c.section}`;
                label = `Page ${c.page_number}, ${sectionStr}`;
              } else if (c.page_number != null) {
                label = `Page ${c.page_number}`;
              } else if (c.section) {
                label = c.section;
              }
            } else {
              if (c.act_name && c.act_section) {
                const sectionStr = c.act_section.toLowerCase().startsWith("section") || c.act_section.toLowerCase().startsWith("clause")
                  ? c.act_section
                  : `Section ${c.act_section}`;
                label = `${c.act_name}, ${sectionStr}`;
              } else if (c.act_name) {
                label = c.act_name;
              } else if (c.act_section) {
                label = c.act_section;
              }
            }

            const textSnippet = c.text.slice(0, 80) + (c.text.length > 80 ? "..." : "");

            return (
              <div
                key={c.chunk_id || index}
                style={{
                  borderLeft: `2px solid ${isDocument ? "#4A9EFF" : "#F5A623"}`,
                  background: "transparent",
                  padding: "8px 12px",
                  marginBottom: "4px",
                  borderRadius: "0 4px 4px 0",
                  display: "flex",
                  flexDirection: "row",
                  alignItems: "baseline",
                  gap: "8px",
                  flexWrap: "wrap",
                }}
              >
                <span style={{ color: "#888888", fontSize: "12px" }} className="shrink-0">
                  {label}
                </span>
                <span style={{ color: "#666666", fontSize: "12px", fontStyle: "italic" }}>
                  {textSnippet}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
