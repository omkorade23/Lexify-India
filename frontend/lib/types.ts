// ── Types exactly matching backend API contracts ────────────────────────

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  num_pages: number;
  extraction_status: "completed" | "failed" | "pending";
  preview_text: string;
  metadata: {
    file_size: number;
    language: string;
    document_type: string;
  };
}

export interface Message {
  role: "user" | "assistant";
  content: string;
}

export interface Citation {
  source_type: "document" | "legal_reference";
  text: string;
  page_number?: number;
  section?: string;
  act_name?: string;
  act_section?: string;
  category?: string;
  similarity_score: number;
  chunk_id: string;
}

export interface QueryRequest {
  document_id: string;
  question: string;
  conversation_history: Message[];
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
  confidence: "high" | "medium" | "low" | "none";
  related_sections: string[];
  has_legal_context: boolean;
}

export interface ApiError {
  message: string;
  status?: number;
}

// ── LocalStorage document registry ─────────────────────────────────────

export interface StoredDocument {
  document_id: string;
  filename: string;
  document_type: string;
  num_pages: number;
  uploaded_at: string; // ISO string
}

// ── Chat message UI model ────────────────────────────────────────────────

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  confidence?: QueryResponse["confidence"];
  has_legal_context?: boolean;
  related_sections?: string[];
  timestamp: Date;
  error?: boolean;
}

// ── Upload state machine ─────────────────────────────────────────────────

export type UploadState =
  | "idle"
  | "selected"
  | "uploading"
  | "processing"
  | "complete"
  | "error";
