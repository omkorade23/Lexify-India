import type {
  DocumentUploadResponse,
  QueryRequest,
  QueryResponse,
  ApiError,
  Message,
} from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── Generic fetch wrapper ────────────────────────────────────────────────

async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${path}`;
  let response: Response;

  try {
    response = await fetch(url, {
      ...options,
      headers: {
        ...options?.headers,
      },
    });
  } catch (networkError) {
    const err: ApiError = {
      message:
        "Unable to connect to the server. Please ensure the backend is running.",
    };
    throw err;
  }

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      message = body.detail ?? body.message ?? message;
    } catch {
      // ignore parse error
    }
    const err: ApiError = { message, status: response.status };
    throw err;
  }

  return response.json() as Promise<T>;
}

// ── API methods ───────────────────────────────────────────────────────────

export async function uploadDocument(
  file: File
): Promise<DocumentUploadResponse> {
  const form = new FormData();
  form.append("file", file);

  return apiFetch<DocumentUploadResponse>("/api/documents/upload", {
    method: "POST",
    body: form,
  });
}

export async function queryDocument(
  request: QueryRequest
): Promise<QueryResponse> {
  return apiFetch<QueryResponse>("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
}

export async function queryLegal(request: {
  question: string;
  conversation_history: Message[];
}): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE}/api/legal-chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(
      error?.detail ?? `Legal chat failed: ${response.status}`
    );
  }

  return response.json();
}

export async function getDocument(documentId: string) {
  return apiFetch<DocumentUploadResponse>(
    `/api/documents/${documentId}`
  );
}

export async function checkHealth(): Promise<{ status: string }> {
  return apiFetch<{ status: string }>("/health");
}
