"use client";

import { useState, useCallback } from "react";
import { uploadDocument } from "@/lib/api";
import { saveDocument } from "@/lib/utils";
import type { DocumentUploadResponse, UploadState } from "@/lib/types";

interface UseDocumentUploadReturn {
  state: UploadState;
  file: File | null;
  result: DocumentUploadResponse | null;
  error: string | null;
  progress: number;
  selectFile: (file: File) => void;
  clearFile: () => void;
  upload: () => Promise<void>;
  reset: () => void;
}

export function useDocumentUpload(): UseDocumentUploadReturn {
  const [state, setState] = useState<UploadState>("idle");
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<DocumentUploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  const selectFile = useCallback((f: File) => {
    setFile(f);
    setState("selected");
    setError(null);
  }, []);

  const clearFile = useCallback(() => {
    setFile(null);
    setState("idle");
    setError(null);
    setProgress(0);
  }, []);

  const upload = useCallback(async () => {
    if (!file) return;
    setState("uploading");
    setProgress(10);
    setError(null);

    try {
      // Simulate progress ticks while the upload is in-flight
      const ticker = setInterval(() => {
        setProgress((p) => Math.min(p + 8, 70));
      }, 400);

      const data = await uploadDocument(file);
      clearInterval(ticker);

      setState("processing");
      setProgress(80);

      // Save to local registry
      saveDocument({
        document_id: data.document_id,
        filename: data.filename,
        document_type: data.metadata?.document_type ?? "unknown",
        num_pages: data.num_pages,
        uploaded_at: new Date().toISOString(),
      });

      // Simulate processing step
      await new Promise((resolve) => setTimeout(resolve, 1500));
      setProgress(100);
      setState("complete");
      setResult(data);
    } catch (err: unknown) {
      const msg =
        err && typeof err === "object" && "message" in err
          ? (err as { message: string }).message
          : "Upload failed. Please try again.";
      setError(msg);
      setState("error");
      setProgress(0);
    }
  }, [file]);

  const reset = useCallback(() => {
    setState("idle");
    setFile(null);
    setResult(null);
    setError(null);
    setProgress(0);
  }, []);

  return { state, file, result, error, progress, selectFile, clearFile, upload, reset };
}
