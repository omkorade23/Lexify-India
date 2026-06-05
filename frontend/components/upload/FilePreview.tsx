import React from "react";
import { FileText, X } from "lucide-react";
import { formatFileSize } from "@/lib/utils";

interface FilePreviewProps {
  file: File;
  onRemove: () => void;
  onUpload: () => void;
  loading?: boolean;
}

export default function FilePreview({
  file,
  onRemove,
  onUpload,
  loading,
}: FilePreviewProps) {
  return (
    <div className="space-y-4">
      {/* File card */}
      <div className="flex items-center gap-4 bg-bg-surface border border-white/[0.08] rounded-xl px-4 py-4">
        <div className="w-10 h-10 rounded-lg bg-[rgba(34,197,94,0.10)] flex items-center justify-center shrink-0">
          <FileText size={20} className="text-accent" />
        </div>

        <div className="flex-1 min-w-0">
          <p className="text-text-primary font-medium text-sm truncate">
            {file.name}
          </p>
          <p className="text-text-secondary text-[12px] mt-0.5">
            {formatFileSize(file.size)} · {file.type || "document"}
          </p>
        </div>

        <button
          onClick={onRemove}
          className="p-1.5 rounded-lg text-text-muted hover:text-text-secondary hover:bg-white/[0.04] transition-colors shrink-0"
          aria-label="Remove file"
        >
          <X size={16} />
        </button>
      </div>

      {/* Upload CTA */}
      <button
        onClick={onUpload}
        disabled={loading}
        className="w-full bg-accent hover:bg-accent-hover disabled:opacity-60 text-[#0A0A0A] font-semibold text-sm py-3 rounded-xl transition-all duration-200 hover:shadow-accent-glow-sm flex items-center justify-center gap-2"
        aria-label="Upload and analyze document"
      >
        {loading ? (
          <>
            <div className="w-4 h-4 border-2 border-[#0A0A0A] border-t-transparent rounded-full animate-spin" />
            Uploading...
          </>
        ) : (
          "Upload and Analyze"
        )}
      </button>
    </div>
  );
}
