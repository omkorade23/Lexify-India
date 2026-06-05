"use client";

import React from "react";
import AppShell from "@/components/layout/AppShell";
import UploadZone from "@/components/upload/UploadZone";
import FilePreview from "@/components/upload/FilePreview";
import ProcessingCard from "@/components/upload/ProcessingCard";
import UploadComplete from "@/components/upload/UploadComplete";
import { useDocumentUpload } from "@/hooks/useDocumentUpload";
import { AlertTriangle } from "lucide-react";

export default function UploadPage() {
  const { state, file, result, error, progress, selectFile, clearFile, upload } =
    useDocumentUpload();

  return (
    <AppShell>
      <div className="flex-1 overflow-y-auto">
        <div className="ambient-glow min-h-full flex items-center justify-center px-6 py-12">
          <div className="w-full max-w-lg">
            {/* Header */}
            {state === "idle" || state === "selected" ? (
              <div className="text-center mb-8">
                <h1 className="text-text-primary text-2xl font-bold mb-2">
                  Upload Legal Document
                </h1>
                <p className="text-text-secondary text-sm">
                  PDF, JPG, or PNG — up to 10 MB. Your document stays private.
                </p>
              </div>
            ) : null}

            {/* State machine rendering */}
            {(state === "idle" || state === "selected") && (
              <div className="space-y-6">
                <UploadZone
                  onFileSelect={selectFile}
                  disabled={state === "selected"}
                />

                {file && state === "selected" && (
                  <FilePreview
                    file={file}
                    onRemove={clearFile}
                    onUpload={upload}
                  />
                )}
              </div>
            )}

            {state === "uploading" && file && (
              <div className="space-y-6">
                <FilePreview
                  file={file}
                  onRemove={clearFile}
                  onUpload={upload}
                  loading
                />
              </div>
            )}

            {(state === "processing" || state === "uploading") && file && (
              <div className="mt-8">
                <ProcessingCard filename={file.name} progress={progress} />
              </div>
            )}

            {state === "complete" && result && (
              <UploadComplete result={result} />
            )}

            {state === "error" && (
              <div
                className="flex flex-col items-center gap-4 text-center py-10"
                role="alert"
              >
                <div className="w-14 h-14 rounded-full bg-danger/10 border border-danger/30 flex items-center justify-center">
                  <AlertTriangle size={24} className="text-danger" />
                </div>
                <div>
                  <p className="text-text-primary font-semibold mb-1">
                    Upload Failed
                  </p>
                  <p className="text-text-secondary text-sm">{error}</p>
                </div>
                <button
                  onClick={clearFile}
                  className="px-5 py-2.5 bg-bg-surface border border-border-hover rounded-xl text-text-body text-sm hover:bg-bg-elevated transition-colors"
                >
                  Try Again
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
