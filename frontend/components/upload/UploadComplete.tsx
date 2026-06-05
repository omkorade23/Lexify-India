import React from "react";
import Link from "next/link";
import { CheckCircle2, FileText, MessageSquare } from "lucide-react";
import type { DocumentUploadResponse } from "@/lib/types";
import { getDocumentTypeLabel } from "@/lib/utils";

interface UploadCompleteProps {
  result: DocumentUploadResponse;
}

export default function UploadComplete({ result }: UploadCompleteProps) {
  return (
    <div
      className="max-w-md w-full mx-auto text-center animate-fade-in"
      role="status"
      aria-live="polite"
    >
      {/* Checkmark */}
      <div className="flex justify-center mb-6">
        <div className="w-16 h-16 rounded-full bg-[rgba(34,197,94,0.10)] border border-[rgba(34,197,94,0.25)] flex items-center justify-center">
          <CheckCircle2 size={32} className="text-accent" />
        </div>
      </div>

      <h2 className="text-text-primary text-xl font-semibold mb-2">
        Document Ready
      </h2>
      <p className="text-text-secondary text-sm mb-6">
        Your document has been processed and is ready for analysis.
      </p>

      {/* Document card */}
      <div className="bg-bg-surface border border-border-default border-l-[3px] border-l-[rgba(34,197,94,0.35)] rounded-xl p-4 text-left mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-9 h-9 rounded-lg bg-[rgba(34,197,94,0.10)] flex items-center justify-center">
            <FileText size={18} className="text-accent" />
          </div>
          <div>
            <p className="text-text-primary font-medium text-sm truncate">
              {result.filename}
            </p>
            <p className="text-text-secondary text-[12px]">
              {getDocumentTypeLabel(result.metadata?.document_type ?? "")} · {result.num_pages} pages
            </p>
          </div>
        </div>
        {result.preview_text && (
          <p className="text-text-secondary text-[13px] leading-relaxed line-clamp-3">
            {result.preview_text}
          </p>
        )}
      </div>

      {/* CTA */}
      <Link
        href={`/chat/${result.document_id}`}
        className="flex items-center justify-center gap-2 w-full bg-accent hover:bg-accent-hover text-[#0A0A0A] font-semibold text-sm py-3 rounded-xl transition-all duration-200 hover:shadow-accent-glow-sm"
        aria-label="Start asking questions about your document"
      >
        <MessageSquare size={16} />
        Start Analyzing
      </Link>
    </div>
  );
}
