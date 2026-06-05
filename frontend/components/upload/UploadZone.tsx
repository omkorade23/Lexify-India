"use client";

import React, { useCallback, useRef, useState } from "react";
import { Upload, FileText } from "lucide-react";
import { cn, formatFileSize } from "@/lib/utils";

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
}

const ACCEPTED_TYPES = [".pdf", ".jpg", ".jpeg", ".png"];
const MAX_SIZE = 10 * 1024 * 1024; // 10 MB

export default function UploadZone({ onFileSelect, disabled }: UploadZoneProps) {
  const [dragOver, setDragOver] = useState(false);
  const [dragError, setDragError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validate = (file: File): string | null => {
    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    if (!ACCEPTED_TYPES.includes(ext)) {
      return `Unsupported file type. Accepted: PDF, JPG, PNG`;
    }
    if (file.size > MAX_SIZE) {
      return `File too large. Maximum size is ${formatFileSize(MAX_SIZE)}`;
    }
    return null;
  };

  const handleFile = useCallback(
    (file: File) => {
      const err = validate(file);
      if (err) {
        setDragError(err);
        return;
      }
      setDragError(null);
      onFileSelect(file);
    },
    [onFileSelect]
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <div
      onClick={() => !disabled && inputRef.current?.click()}
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragLeave={() => setDragOver(false)}
      className={cn(
        "relative flex flex-col items-center justify-center gap-5 rounded-2xl cursor-pointer transition-all duration-200",
        "min-h-[280px] px-8 py-12",
        dragOver
          ? "border-[1.5px] border-accent bg-[rgba(34,197,94,0.04)]"
          : "border-[1.5px] border-dashed border-white/[0.10] bg-white/[0.02]",
        "hover:border-white/[0.18] hover:bg-white/[0.03]",
        disabled && "opacity-50 cursor-not-allowed"
      )}
      role="button"
      tabIndex={0}
      aria-label="Upload zone — click or drag a file here"
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_TYPES.join(",")}
        onChange={onInputChange}
        className="hidden"
        aria-hidden="true"
      />

      {/* Icon */}
      <div className="w-16 h-16 rounded-2xl bg-bg-surface border border-border-default flex items-center justify-center">
        <Upload size={28} className="text-text-secondary" />
      </div>

      {/* Text */}
      <div className="text-center">
        <p className="text-text-body font-medium text-[15px] mb-1">
          {dragOver ? "Drop your document here" : "Click to upload or drag & drop"}
        </p>
        <p className="text-text-muted text-[13px]">
          Supports PDF, JPG, PNG — up to {formatFileSize(MAX_SIZE)}
        </p>
      </div>

      {/* File type chips */}
      <div className="flex items-center gap-2 flex-wrap justify-center">
        {["PDF", "JPG", "PNG"].map((type) => (
          <span
            key={type}
            className="flex items-center gap-1 px-3 py-1 rounded-full text-[11px] text-text-secondary bg-white/[0.06] border border-white/[0.08]"
          >
            <FileText size={10} />
            {type}
          </span>
        ))}
      </div>

      {/* Error */}
      {dragError && (
        <p className="text-danger text-[13px] text-center">{dragError}</p>
      )}
    </div>
  );
}
