import React from "react";
import { User } from "lucide-react";
import { cn } from "@/lib/utils";

interface MessageBubbleProps {
  content: string;
  timestamp: Date;
  error?: boolean;
}

export default function MessageBubble({
  content,
  timestamp,
  error,
}: MessageBubbleProps) {
  return (
    <div className="flex items-start justify-end gap-2 animate-fade-in">
      {/* Bubble */}
      <div className="flex flex-col items-end gap-1 max-w-[72%]">
        <div
          className={cn(
            "bg-bg-surface border rounded-[14px] px-5 py-[18px] text-text-body text-[14px] leading-relaxed",
            error ? "border-danger/30 bg-danger/10" : "border-border-default"
          )}
        >
          {content}
        </div>
        <span className="text-[10px] text-text-placeholder px-1">
          {timestamp.toLocaleTimeString("en-IN", {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>

      {/* Avatar */}
      <div className="w-9 h-9 rounded-full bg-bg-elevated flex items-center justify-center shrink-0 mt-0.5">
        <User size={16} className="text-text-secondary" />
      </div>
    </div>
  );
}
