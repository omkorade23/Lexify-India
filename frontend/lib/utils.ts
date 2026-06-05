import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import type { StoredDocument } from "./types";

// ── Tailwind class merger ─────────────────────────────────────────────────

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

// ── LocalStorage document registry ───────────────────────────────────────

const LS_KEY = "lexify_documents";

export function getStoredDocuments(): StoredDocument[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as StoredDocument[];
  } catch {
    return [];
  }
}

export function saveDocument(doc: StoredDocument): void {
  if (typeof window === "undefined") return;
  const docs = getStoredDocuments();
  const existing = docs.findIndex((d) => d.document_id === doc.document_id);
  if (existing >= 0) {
    docs[existing] = doc;
  } else {
    docs.unshift(doc);
  }
  localStorage.setItem(LS_KEY, JSON.stringify(docs));
}

export function clearDocuments(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(LS_KEY);
}

// ── Formatting helpers ────────────────────────────────────────────────────

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function formatRelativeTime(iso: string): string {
  const now = Date.now();
  const then = new Date(iso).getTime();
  const diff = now - then;

  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return formatDate(iso);
}

export function getDocumentTypeLabel(type: string): string {
  const map: Record<string, string> = {
    rental_agreement: "Rental Agreement",
    employment_contract: "Employment Contract",
    nda: "NDA",
    property_deed: "Property Deed",
    legal_notice: "Legal Notice",
    affidavit: "Affidavit",
    power_of_attorney: "Power of Attorney",
    sale_deed: "Sale Deed",
    partnership_deed: "Partnership Deed",
  };
  return map[type] ?? type.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function generateId(): string {
  return Math.random().toString(36).slice(2, 11);
}
