"use client";

import React, { useState, useRef, useEffect } from "react";
import { Paperclip, Send } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (message: string) => void;
  loading?: boolean;
  disabled?: boolean;
  placeholder?: string;
  /** Pre-fill the input with this text (e.g. from chip click) */
  prefill?: string;
  /** Called after prefill has been consumed so parent can reset */
  onPrefillConsumed?: () => void;
}

export default function ChatInput({
  onSend,
  loading = false,
  disabled = false,
  placeholder = "Ask a question about your document...",
  prefill,
  onPrefillConsumed,
}: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Apply prefill when it changes
  useEffect(() => {
    if (prefill) {
      setValue(prefill);
      textareaRef.current?.focus();
      onPrefillConsumed?.();
    }
  }, [prefill, onPrefillConsumed]);

  // Auto-resize textarea — single line default, expands to max-height
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 200) + "px";
  }, [value]);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || loading || disabled) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    /* Outer wrapper: full-width, bg prevents scroll bleed-through */
    <div
      className="shrink-0 w-full bg-bg-base"
      style={{
        paddingTop: "16px",
        paddingBottom: "24px",
      }}
    >
      {/* Constrained inner column — matches 760px conversation column */}
      <div
        style={{
          maxWidth: "760px",
          margin: "0 auto",
          paddingLeft: "24px",
          paddingRight: "24px",
        }}
      >
        {/*
         * Pill-shaped input container.
         * No border in any state — avoids green rectangle on focus.
         * Background is constant; no React focus state drives visual changes.
         */}
        <div
          className="flex items-center gap-3 bg-bg-input"
          style={{
            minHeight: "52px",
            borderRadius: "26px",
            padding: "14px 20px",
          }}
        >
          {/* Attachment icon */}
          <button
            className="shrink-0 transition-colors"
            aria-label="Attach file"
            type="button"
            style={{ color: "#4A4A4A", outline: "none" }}
            onMouseOver={(e) =>
              ((e.currentTarget as HTMLElement).style.color = "#888888")
            }
            onMouseOut={(e) =>
              ((e.currentTarget as HTMLElement).style.color = "#4A4A4A")
            }
          >
            <Paperclip size={20} />
          </button>

          {/*
           * Textarea.
           * outline: none — overrides the global *:focus-visible rule in globals.css
           * so the browser does not render a green outline when this element is focused.
           */}
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            rows={1}
            disabled={disabled || loading}
            className="flex-1 bg-transparent text-text-body placeholder:text-text-placeholder text-sm resize-none leading-relaxed overflow-y-auto"
            style={{ maxHeight: "200px", outline: "none" }}
            aria-label="Chat message input"
            aria-live="polite"
          />

          {/* Send button — 36px circle */}
          <button
            onClick={handleSend}
            disabled={!value.trim() || loading || disabled}
            className={cn(
              "shrink-0 flex items-center justify-center rounded-full transition-all duration-200",
              value.trim() && !loading && !disabled
                ? "cursor-pointer"
                : "cursor-not-allowed"
            )}
            style={{
              width: "36px",
              height: "36px",
              outline: "none",
              background:
                value.trim() && !loading && !disabled
                  ? "#22C55E"
                  : "rgba(255,255,255,0.06)",
              color:
                value.trim() && !loading && !disabled ? "#0A0A0A" : "#4A4A4A",
            }}
            onMouseOver={(e) => {
              if (value.trim() && !loading && !disabled) {
                (e.currentTarget as HTMLElement).style.background = "#16A34A";
                (e.currentTarget as HTMLElement).style.boxShadow =
                  "0 0 12px rgba(34,197,94,0.30)";
              }
            }}
            onMouseOut={(e) => {
              if (value.trim() && !loading && !disabled) {
                (e.currentTarget as HTMLElement).style.background = "#22C55E";
                (e.currentTarget as HTMLElement).style.boxShadow = "none";
              }
            }}
            aria-label="Send message"
            type="button"
          >
            {loading ? (
              <div
                className="rounded-full animate-spin"
                style={{
                  width: "14px",
                  height: "14px",
                  border: "2px solid #0A0A0A",
                  borderTopColor: "transparent",
                }}
              />
            ) : (
              <Send size={16} />
            )}
          </button>
        </div>

        {/* Disclaimer */}
        <p
          className="text-center mt-2"
          style={{ fontSize: "11px", color: "#4A4A4A" }}
        >
          Lexify India provides AI-assisted legal information, not legal advice.
          Always consult a qualified lawyer.
        </p>
      </div>
    </div>
  );
}
