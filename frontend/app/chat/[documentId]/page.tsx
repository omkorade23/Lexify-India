"use client";

import React, { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import BottomNav from "@/components/layout/BottomNav";
import MobileDrawer from "@/components/layout/MobileDrawer";
import ChatInput from "@/components/chat/ChatInput";
import MessageBubble from "@/components/chat/MessageBubble";
import AIResponseBlock from "@/components/chat/AIResponseBlock";
import ConversationTimestamp from "@/components/chat/ConversationTimestamp";
import SuggestedChips from "@/components/chat/SuggestedChips";
import { useChat } from "@/hooks/useChat";
import { getStoredDocuments, getDocumentTypeLabel } from "@/lib/utils";
import type { StoredDocument } from "@/lib/types";
import {
  Download,
  Share2,
  MoreHorizontal,
  Search,
  Scale,
} from "lucide-react";
import { cn } from "@/lib/utils";
import ConfidenceBadge from "@/components/chat/ConfidenceBadge";

// Shared conversation column constraint
const COL_MAX = "760px";
const COL_PADDING = "24px";

const SUGGESTED_QUESTIONS = [
  "What is the lock-in period?",
  "What are the payment terms?",
  "What happens if I terminate early?",
  "What are my rights under this agreement?",
];

export default function ChatPage() {
  const { documentId } = useParams<{ documentId: string }>();
  const { messages, loading, sendMessage } = useChat();
  const [doc, setDoc] = useState<StoredDocument | null>(null);
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
  const [tabletExpanded, setTabletExpanded] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const docs = getStoredDocuments();
    const found = docs.find((d) => d.document_id === documentId);
    if (found) setDoc(found);
  }, [documentId]);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = (question: string) => {
    if (documentId) sendMessage(question, documentId);
  };

  // Determine last AI message for confidence badge in top bar
  const lastAIMessage = [...messages].reverse().find((m) => m.role === "assistant");

  return (
    <div className="flex h-screen bg-bg-base overflow-hidden">
      {/* ── Desktop Sidebar (268px) ─────────────────────────────── */}
      <div className="hidden xl:flex flex-col w-[268px] shrink-0 h-full bg-bg-sidebar border-r border-border-default">
        <Sidebar className="w-full h-full" />

        {/* Document-specific sidebar additions */}
        <div className="px-3 py-3 border-t border-border-default space-y-3">
          {/* Search in document */}
          <div className="relative">
            <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-text-placeholder" />
            <input
              placeholder="Search in document..."
              className="w-full bg-bg-surface border border-border-default rounded-lg pl-7 pr-3 py-2 text-[12px] text-text-body placeholder:text-text-placeholder focus:border-accent focus:outline-none transition-colors"
              aria-label="Search in document"
            />
          </div>

          {/* This document */}
          {doc && (
            <div>
              <p className="label-caps px-1 mb-2">This Document</p>
              <div
                className="bg-bg-surface rounded-lg p-3 border border-[rgba(34,197,94,0.18)]"
                style={{ borderLeft: "2px solid rgba(34,197,94,0.35)" }}
              >
                <p className="text-text-primary text-[12px] font-medium truncate mb-2">
                  {doc.filename}
                </p>
                <div className="flex flex-wrap gap-1.5">
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-[rgba(34,197,94,0.10)] text-accent">
                    {getDocumentTypeLabel(doc.document_type)}
                  </span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-[rgba(34,197,94,0.10)] text-accent">
                    {doc.num_pages} Pages
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Conversations */}
          <div>
            <p className="label-caps px-1 mb-2">Conversations</p>
            <button
              className="w-full text-left rounded-lg px-3 py-2 bg-bg-elevated border-l-[2px] border-accent text-text-primary text-[12px] font-medium"
              aria-current="page"
            >
              Current session
            </button>
          </div>
        </div>
      </div>

      {/* ── Tablet sidebar ──────────────────────────────────────── */}
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

      {/* ── Main content panel ──────────────────────────────────── */}
      <div className="flex-1 min-w-0 flex flex-col h-full overflow-hidden relative">
        {/* Ambient glow fills the full panel */}
        <div className="absolute inset-0 ambient-glow pointer-events-none" aria-hidden="true" />

        {/* ── Top bar — document name, type badge, confidence, actions ── */}
        <header className="relative z-10 flex items-center gap-3 px-6 py-4 border-b border-border-default bg-bg-base shrink-0">
          <Scale size={16} className="text-accent shrink-0 hidden md:block" />

          {/* Document name + type badge */}
          <div className="flex items-center gap-2 min-w-0 flex-1">
            <p className="text-text-primary font-semibold text-sm truncate">
              {doc?.filename ?? "Chat Workspace"}
            </p>
            {doc && (
              <span
                className="inline-flex text-[10px] font-medium px-2 py-0.5 rounded shrink-0"
                style={{
                  background: "rgba(34,197,94,0.10)",
                  border: "1px solid rgba(34,197,94,0.20)",
                  color: "#22C55E",
                }}
              >
                {getDocumentTypeLabel(doc.document_type)}
              </span>
            )}
          </div>

          {/* Confidence badge */}
          {lastAIMessage?.confidence && (
            <ConfidenceBadge confidence={lastAIMessage.confidence} />
          )}

          {/* Action icons */}
          <div className="flex items-center gap-2 shrink-0">
            <button
              className="p-2 rounded-lg text-text-secondary hover:text-text-body hover:bg-white/[0.04] transition-colors"
              aria-label="Download document"
            >
              <Download size={16} />
            </button>
            <button
              className="p-2 rounded-lg text-text-secondary hover:text-text-body hover:bg-white/[0.04] transition-colors"
              aria-label="Share conversation"
            >
              <Share2 size={16} />
            </button>
            <button
              className="p-2 rounded-lg text-text-secondary hover:text-text-body hover:bg-white/[0.04] transition-colors"
              aria-label="More options"
            >
              <MoreHorizontal size={16} />
            </button>
          </div>
        </header>

        {/* ── Scrollable message area ─────────────────────────── */}
        <div
          className="relative z-10 flex-1 overflow-y-auto"
          role="log"
          aria-label="Conversation"
          aria-live="polite"
        >
          {messages.length === 0 ? (
            /* ── Empty state ─────────────────────────────────── */
            <div className="flex flex-col items-center justify-center h-full">
              {/* Constrained column */}
              <div
                style={{
                  maxWidth: COL_MAX,
                  width: "100%",
                  paddingLeft: COL_PADDING,
                  paddingRight: COL_PADDING,
                }}
              >
                <div className="text-center" style={{ marginBottom: "32px" }}>
                  <div
                    className="rounded-full flex items-center justify-center mx-auto"
                    style={{
                      width: "64px",
                      height: "64px",
                      background: "rgba(34,197,94,0.12)",
                      border: "1px solid rgba(34,197,94,0.25)",
                      marginBottom: "16px",
                    }}
                  >
                    <Scale size={28} className="text-accent" />
                  </div>
                  <h2
                    className="text-text-primary font-semibold"
                    style={{ fontSize: "20px", marginBottom: "8px" }}
                  >
                    {doc ? `Analyzing ${doc.filename}` : "Start a Conversation"}
                  </h2>
                  <p className="text-text-secondary text-sm">
                    Ask any question about your document to get started
                  </p>
                </div>

                {/* 2×2 suggestion chip grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {SUGGESTED_QUESTIONS.map((q) => (
                    <button
                      key={q}
                      onClick={() => handleSend(q)}
                      className="text-left px-4 py-3 rounded-xl text-[13px] text-text-secondary border border-white/[0.08] bg-white/[0.04] hover:bg-[rgba(34,197,94,0.08)] hover:border-[rgba(34,197,94,0.20)] hover:text-text-body transition-all duration-200"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* ── Active message thread ────────────────────────── */
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

              <div className="space-y-0">
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
                      {/* Suggested follow-ups aligned to AI text indent */}
                      {!msg.error &&
                        msg.related_sections &&
                        msg.related_sections.length > 0 && (
                          <SuggestedChips
                            chips={msg.related_sections.slice(0, 3)}
                            onSelect={handleSend}
                          />
                        )}
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

        {/* ── Composer — constrained, anchored to bottom ─────── */}
        <ChatInput
          onSend={handleSend}
          loading={loading}
          disabled={!documentId}
        />
      </div>

      {/* ── Mobile nav ─────────────────────────────────────────── */}
      <BottomNav onHamburger={() => setMobileDrawerOpen(true)} />
      <MobileDrawer open={mobileDrawerOpen} onClose={() => setMobileDrawerOpen(false)} />
    </div>
  );
}
