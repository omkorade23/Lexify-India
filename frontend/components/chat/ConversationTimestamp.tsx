import React from "react";

interface ConversationTimestampProps {
  date: Date;
}

export default function ConversationTimestamp({
  date,
}: ConversationTimestampProps) {
  const formatted = date.toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <div className="flex items-center justify-center my-4" role="separator" aria-label={formatted}>
      <div className="h-px flex-1 bg-border-default" />
      <span className="mx-4 text-[11px] text-text-placeholder whitespace-nowrap">
        {formatted}
      </span>
      <div className="h-px flex-1 bg-border-default" />
    </div>
  );
}
