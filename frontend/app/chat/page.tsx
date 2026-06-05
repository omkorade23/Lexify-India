"use client";

import React, { useEffect, useRef, useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import BottomNav from "@/components/layout/BottomNav";
import MobileDrawer from "@/components/layout/MobileDrawer";
import ChatInput from "@/components/chat/ChatInput";
import MessageBubble from "@/components/chat/MessageBubble";
import AIResponseBlock from "@/components/chat/AIResponseBlock";
import ConversationTimestamp from "@/components/chat/ConversationTimestamp";
import { useChat } from "@/hooks/useChat";
import { getStoredDocuments } from "@/lib/utils";
import type { StoredDocument } from "@/lib/types";
import { Scale, Upload, FolderOpen } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

const EXAMPLE_CHIPS = [
  "What is anticipatory bail?",
  "Tenant rights in India",
  "What is a legal notice?",
  "Section 138 NI Act",
];

const DOC_TYPES =
  "Rental Agreements · Employment Contracts · NDAs · Legal Notices · Service Agreements";

// Shared max-width for the conversation column
const COL_MAX = "760px";
const COL_PADDING = "24px";

export default function GeneralChatPage() {
  const { messages, loading, sendMessage } = useChat();
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
  const [tabletExpanded, setTabletExpanded] = useState(false);
  const [inputPrefill, setInputPrefill] = useState("");
  const [recentDocs, setRecentDocs] = useState<StoredDocument[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    setRecentDocs(getStoredDocuments().slice(0, 3));
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = (question: string) => {
    sendMessage(question, null);
    setInputPrefill("");
  };

  const handleChipClick = (chip: string) => {
    setInputPrefill(chip);
  };

  const isEmptyState = messages.length === 0;

  return (
    <div className="flex h-screen bg-bg-base overflow-hidden">
      {/* ── Desktop Sidebar ─────────────────────────────────────── */}
      <div className="hidden xl:flex flex-col w-[268px] shrink-0 h-full bg-bg-sidebar border-r border-border-default">
        <Sidebar className="w-full h-full" />
      </div>

      {/* ── Tablet sidebar icon-rail ─────────────────────────────── */}
      <div
        className="hidden md:flex xl:hidden shrink-0 h-full relative z-30"
        style={{ width: tabletExpanded ? 240 : 64 }}
        onMouseEnter={() => setTabletExpanded(true)}
        onMouseLeave={() => setTabletExpanded(false)}
      >
        <Sidebar
          collapsed={!tabletExpanded}
          className={
            tabletExpanded
              ? "w-60 shadow-2xl absolute left-0 top-0 bottom-0 z-40"
              : "w-16"
          }
        />
      </div>

      {/* ── Main content panel — full width of remaining space ──── */}
      <div className="flex-1 min-w-0 flex flex-col h-full overflow-hidden relative">
        {/* Ambient glow fills the full panel */}
        <div className="absolute inset-0 ambient-glow pointer-events-none" aria-hidden="true" />

        {/* ── Top bar: quiet chrome, Upload Doc button only ─────── */}
        <header className="relative z-10 flex items-center px-6 py-4 border-b border-border-default bg-bg-base shrink-0">
          {/* Empty spacer — no title label on general chat page */}
          <div className="flex-1" />
          <Link
            href="/upload"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-text-secondary hover:text-text-body hover:bg-white/[0.04] border border-border-default text-[12px] font-medium transition-all"
            aria-label="Upload a document"
          >
            <Upload size={13} />
            <span className="hidden sm:inline">Upload Doc</span>
          </Link>
        </header>

        {/* ── Scrollable area: message feed OR empty state ─────── */}
        <div
          className="relative z-10 flex-1 overflow-y-auto"
          role="log"
          aria-label="Conversation"
          aria-live="polite"
        >
          {isEmptyState ? (
            /* ── Empty state — vertically centered ──────────────── */
            <div
              className="flex flex-col items-center justify-center min-h-full"
              style={{
                padding: `0 ${COL_PADDING}`,
              }}
            >
              {/* Inner column constrained to 760px */}
              <div style={{ maxWidth: COL_MAX, width: "100%" }}>
                {/* Logo + heading + subheading */}
                <div
                  className="flex flex-col items-center text-center"
                  style={{ marginBottom: "32px" }}
                >
                  <div
                    className="rounded-2xl flex items-center justify-center"
                    style={{
                      width: "52px",
                      height: "52px",
                      background: "rgba(34,197,94,0.12)",
                      border: "1px solid rgba(34,197,94,0.25)",
                      marginBottom: "24px",
                    }}
                  >
                    <Scale size={24} className="text-accent" />
                  </div>

                  <h1
                    className="font-semibold"
                    style={{ color: "#ffffff", fontSize: "24px", marginBottom: "12px" }}
                  >
                    How can I help you today?
                  </h1>
                  <p style={{ color: "#888888", fontSize: "15px" }}>
                    Ask any legal question, or upload a document for analysis.
                  </p>
                </div>

                {/* Two option cards — side-by-side on desktop, stacked on mobile */}
                <div
                  className="flex flex-col sm:flex-row"
                  style={{ gap: "16px", marginTop: "32px" }}
                >
                  {/* Card 1 — Ask a Legal Question */}
                  <div
                    className="flex flex-col gap-3 rounded-xl"
                    style={{
                      flex: 1,
                      maxWidth: "380px",
                      background: "#252525",
                      border: "1px solid rgba(34,197,94,0.25)",
                      borderLeft: "3px solid #22C55E",
                      padding: "24px",
                    }}
                  >
                    <div className="flex items-center gap-3">
                      <Scale size={20} className="text-accent shrink-0" />
                      <p className="font-semibold" style={{ color: "#ffffff", fontSize: "15px" }}>
                        Ask a Legal Question
                      </p>
                    </div>
                    <p style={{ color: "#888888", fontSize: "13px", lineHeight: 1.6 }}>
                      Get answers about Indian law, rights, and legal procedures.
                    </p>
                    {/* Example chips — max 4, wrapping up to 2 rows */}
                    <div className="flex flex-wrap" style={{ gap: "8px", marginTop: "16px" }}>
                      {EXAMPLE_CHIPS.map((chip) => (
                        <button
                          key={chip}
                          onClick={() => handleChipClick(chip)}
                          className="transition-all"
                          style={{
                            background: "rgba(34,197,94,0.08)",
                            border: "1px solid rgba(34,197,94,0.20)",
                            borderRadius: "20px",
                            padding: "5px 12px",
                            color: "#EFEFEF",
                            fontSize: "12px",
                            cursor: "pointer",
                            width: "fit-content",
                          }}
                          aria-label={`Ask: ${chip}`}
                        >
                          {chip}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Card 2 — Analyze a Document */}
                  <div
                    className="flex flex-col gap-3 rounded-xl"
                    style={{
                      flex: 1,
                      maxWidth: "380px",
                      background: "#252525",
                      border: "1px solid rgba(255,255,255,0.08)",
                      padding: "24px",
                    }}
                  >
                    <div className="flex items-center gap-3">
                      <FolderOpen size={20} style={{ color: "#888888" }} className="shrink-0" />
                      <p className="font-semibold" style={{ color: "#EFEFEF", fontSize: "15px" }}>
                        Analyze a Document
                      </p>
                    </div>
                    <p style={{ color: "#888888", fontSize: "13px", lineHeight: 1.6 }}>
                      Upload a rental agreement, NDA, employment contract, or other
                      legal document for clause-by-clause analysis.
                    </p>
                    <p style={{ color: "#666666", fontSize: "12px" }}>{DOC_TYPES}</p>
                    <Link
                      href="/upload"
                      className="inline-flex items-center gap-2 font-semibold transition-all hover:opacity-90"
                      style={{
                        background: "#22C55E",
                        color: "#0A0A0A",
                        borderRadius: "8px",
                        padding: "10px 20px",
                        fontSize: "14px",
                        fontWeight: 600,
                        width: "fit-content",
                        marginTop: "4px",
                      }}
                      aria-label="Upload a document"
                    >
                      <Upload size={15} />
                      Upload Document
                    </Link>
                  </div>
                </div>

                {/* Recent docs shortcut */}
                {recentDocs.length > 0 && (
                  <div style={{ marginTop: "32px" }}>
                    <p className="label-caps mb-3" style={{ color: "#666666" }}>
                      Recent Documents
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {recentDocs.map((doc) => (
                        <button
                          key={doc.document_id}
                          onClick={() => router.push(`/chat/${doc.document_id}`)}
                          className="flex items-center gap-2 px-3 py-2 rounded-lg text-[13px] transition-all hover:opacity-90"
                          style={{
                            background: "#252525",
                            border: "1px solid rgba(255,255,255,0.08)",
                            color: "#888888",
                          }}
                          aria-label={`Open ${doc.filename}`}
                        >
                          <FolderOpen size={13} />
                          <span className="truncate" style={{ maxWidth: "160px" }}>
                            {doc.filename}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            /* ── Active chat feed ─────────────────────────────────── */
            <div
              style={{
                maxWidth: COL_MAX,
                margin: "0 auto",
                paddingLeft: COL_PADDING,
                paddingRight: COL_PADDING,
                paddingTop: "32px",
                paddingBottom: "120px",
              }}
            >
              <ConversationTimestamp date={messages[0].timestamp} />

              <div className="space-y-6">
                {messages.map((msg) =>
                  msg.role === "user" ? (
                    <div key={msg.id} style={{ marginBottom: "24px" }}>
                      <MessageBubble
                        content={msg.content}
                        timestamp={msg.timestamp}
                        error={msg.error}
                      />
                    </div>
                  ) : (
                    <div key={msg.id} style={{ marginBottom: "32px" }}>
                      <AIResponseBlock message={msg} />
                    </div>
                  )
                )}

                {/* Loading dots */}
                {loading && (
                  <div className="flex items-start gap-3 animate-fade-in">
                    <div
                      className="rounded-full flex items-center justify-center shrink-0"
                      style={{
                        width: "36px",
                        height: "36px",
                        background: "rgba(34,197,94,0.12)",
                        border: "1px solid rgba(34,197,94,0.25)",
                      }}
                    >
                      <Scale size={15} className="text-accent animate-pulse" />
                    </div>
                    <div className="flex items-center gap-1.5 pt-3">
                      {[0, 1, 2].map((i) => (
                        <span
                          key={i}
                          className="w-2 h-2 rounded-full bg-text-muted animate-bounce"
                          style={{ animationDelay: `${i * 0.15}s` }}
                        />
                      ))}
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            </div>
          )}
        </div>

        {/* ── Composer — constrained to 760px, anchored bottom ──── */}
        <ChatInput
          onSend={handleSend}
          loading={loading}
          placeholder="Ask any legal question..."
          prefill={inputPrefill}
          onPrefillConsumed={() => setInputPrefill("")}
        />
      </div>

      {/* ── Mobile nav ──────────────────────────────────────────── */}
      <BottomNav onHamburger={() => setMobileDrawerOpen(true)} />
      <MobileDrawer
        open={mobileDrawerOpen}
        onClose={() => setMobileDrawerOpen(false)}
      />
    </div>
  );
}
