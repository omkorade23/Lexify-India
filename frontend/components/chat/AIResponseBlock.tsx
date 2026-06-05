import React from "react";
import { Scale, AlertTriangle } from "lucide-react";
import type { ChatMessage } from "@/lib/types";
import SourcesSection from "./SourcesSection";
import ConfidenceBadge from "./ConfidenceBadge";
import LegalContextBadge from "./LegalContextBadge";
import { cn } from "@/lib/utils";

interface AIResponseBlockProps {
  message: ChatMessage;
}

export default function AIResponseBlock({ message }: AIResponseBlockProps) {
  return (
    <div className="flex items-start gap-3 animate-fade-in">
      {/* Avatar */}
      <div className="w-9 h-9 rounded-full bg-[rgba(34,197,94,0.12)] border border-[rgba(34,197,94,0.25)] flex items-center justify-center shrink-0 mt-0.5">
        {message.error ? (
          <AlertTriangle size={15} className="text-warning" />
        ) : (
          <Scale size={15} className="text-accent" />
        )}
      </div>

      {/* Content — fills column width minus avatar+gap */}
      <div className="flex-1 min-w-0">
        {/* Badges row */}
        {!message.error && (message.confidence || message.has_legal_context) && (
          <div className="flex flex-wrap items-center gap-2 mb-3">
            {message.confidence && (
              <ConfidenceBadge confidence={message.confidence} />
            )}
            {message.has_legal_context && <LegalContextBadge />}
          </div>
        )}

        {/* Answer text */}
        <div
          className={cn(
            "text-[14px] leading-relaxed",
            message.error ? "text-warning" : "text-text-body"
          )}
        >
          {message.content.split("\n").map((line, i) => (
            <p key={i} className={i > 0 ? "mt-2" : ""}>
              {line}
            </p>
          ))}
        </div>

        {/* Sources */}
        {!message.error && message.citations && message.citations.length > 0 && (
          <SourcesSection citations={message.citations} />
        )}

        <span className="text-[10px] text-text-placeholder mt-2 block">
          {message.timestamp.toLocaleTimeString("en-IN", {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>
    </div>
  );
}
