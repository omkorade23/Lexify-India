"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import AppShell from "@/components/layout/AppShell";
import { getStoredDocuments } from "@/lib/utils";
import type { StoredDocument } from "@/lib/types";
import { FileText, MessageSquare } from "lucide-react";
import Link from "next/link";
import { getDocumentTypeLabel } from "@/lib/utils";

export default function DocumentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [doc, setDoc] = useState<StoredDocument | null>(null);

  useEffect(() => {
    const docs = getStoredDocuments();
    const found = docs.find((d) => d.document_id === id);
    if (found) {
      setDoc(found);
    }
  }, [id]);

  if (!doc) {
    return (
      <AppShell>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <FileText size={40} className="text-text-placeholder mx-auto mb-3" />
            <p className="text-text-secondary">Document not found</p>
            <Link href="/documents" className="text-accent text-sm mt-2 inline-block hover:underline">
              Back to Documents
            </Link>
          </div>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="flex-1 overflow-y-auto ambient-glow px-8 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-bg-surface border border-border-default rounded-2xl p-6">
            <div className="flex items-start gap-4 mb-6">
              <div className="w-12 h-12 rounded-xl bg-[rgba(34,197,94,0.10)] flex items-center justify-center">
                <FileText size={24} className="text-accent" />
              </div>
              <div>
                <h1 className="text-text-primary text-lg font-bold">{doc.filename}</h1>
                <p className="text-text-secondary text-sm mt-0.5">
                  {getDocumentTypeLabel(doc.document_type)} · {doc.num_pages} pages
                </p>
              </div>
            </div>

            <Link
              href={`/chat/${doc.document_id}`}
              className="flex items-center justify-center gap-2 w-full bg-accent hover:bg-accent-hover text-[#0A0A0A] font-semibold py-3 rounded-xl transition-all duration-200 hover:shadow-accent-glow-sm"
            >
              <MessageSquare size={16} />
              Start Analyzing
            </Link>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
