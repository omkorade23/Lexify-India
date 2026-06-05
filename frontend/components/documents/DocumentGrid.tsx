import React from "react";
import type { StoredDocument } from "@/lib/types";
import DocumentCard from "./DocumentCard";
import { FileText } from "lucide-react";
import Link from "next/link";

interface DocumentGridProps {
  documents: StoredDocument[];
}

export default function DocumentGrid({ documents }: DocumentGridProps) {
  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <div className="w-16 h-16 rounded-2xl bg-bg-surface flex items-center justify-center">
          <FileText size={28} className="text-text-placeholder" />
        </div>
        <p className="text-text-secondary font-medium">No documents found</p>
        <p className="text-text-muted text-sm">
          Upload a document to get started
        </p>
        <Link
          href="/upload"
          className="mt-2 px-4 py-2 bg-accent hover:bg-accent-hover text-[#0A0A0A] text-sm font-semibold rounded-lg transition-colors"
        >
          Upload Document
        </Link>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {documents.map((doc) => (
        <DocumentCard key={doc.document_id} document={doc} />
      ))}
    </div>
  );
}
