"use client";

import React from "react";
import Link from "next/link";
import { FileText, Calendar, FileSearch } from "lucide-react";
import type { StoredDocument } from "@/lib/types";
import DocumentTypeBadge from "./DocumentTypeBadge";
import { formatDate } from "@/lib/utils";

interface DocumentCardProps {
  document: StoredDocument;
}

export default function DocumentCard({ document: doc }: DocumentCardProps) {
  return (
    <Link
      href={`/chat/${doc.document_id}`}
      className="group relative flex flex-col gap-4 bg-bg-surface border border-border-default rounded-2xl p-5 hover:bg-bg-elevated hover:border-border-hover transition-all duration-200"
      aria-label={`Open ${doc.filename}`}
    >
      {/* Type badge top-right */}
      <div className="absolute top-4 right-4">
        <DocumentTypeBadge type={doc.document_type} />
      </div>

      {/* Icon */}
      <div className="w-11 h-11 rounded-xl bg-[rgba(34,197,94,0.10)] flex items-center justify-center">
        <FileText size={22} className="text-accent" />
      </div>

      {/* Title */}
      <div className="flex-1 min-w-0 pr-20">
        <p className="text-text-primary font-semibold text-[14px] truncate mb-1">
          {doc.filename}
        </p>
        <p className="text-text-secondary text-[12px]">
          {doc.num_pages} {doc.num_pages === 1 ? "page" : "pages"}
        </p>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5 text-text-muted text-[12px]">
          <Calendar size={11} />
          <span>{formatDate(doc.uploaded_at)}</span>
        </div>
        <span className="flex items-center gap-1 text-accent text-[12px] opacity-0 group-hover:opacity-100 transition-opacity">
          <FileSearch size={12} />
          Analyze
        </span>
      </div>
    </Link>
  );
}
