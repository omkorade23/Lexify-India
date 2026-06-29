"use client";

import { useState, useCallback } from "react";
import { queryDocument, queryLegal } from "@/lib/api";
import { generateId } from "@/lib/utils";
import type { ChatMessage, Message } from "@/lib/types";

interface UseChatReturn {
  messages: ChatMessage[];
  loading: boolean;
  error: string | null;
  sendMessage: (question: string, documentId?: string | null) => Promise<void>;
  clearMessages: () => void;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (question: string, documentId?: string | null) => {
      if (!question.trim() || loading) return;

      // Append user message immediately
      const userMsg: ChatMessage = {
        id: generateId(),
        role: "user",
        content: question.trim(),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMsg]);
      setLoading(true);
      setError(null);

      // Build conversation history for the API (exclude the latest user msg)
      const history: Message[] = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      try {
        let data;
        if (documentId) {
          data = await queryDocument({
            document_id: documentId,
            question: question.trim(),
            conversation_history: history,
          });
        } else {
          data = await queryLegal({
            question: question.trim(),
            conversation_history: history,
          });
        }

        const assistantMsg: ChatMessage = {
          id: generateId(),
          role: "assistant",
          content: data.answer,
          citations: data.citations,
          confidence: data.confidence,
          has_legal_context: data.has_legal_context,
          related_sections: data.related_sections,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, assistantMsg]);
      } catch (err: unknown) {
        const msg =
          err && typeof err === "object" && "message" in err
            ? (err as { message: string }).message
            : "Failed to get a response. Please try again.";

        const errorMsg: ChatMessage = {
          id: generateId(),
          role: "assistant",
          content: msg,
          timestamp: new Date(),
          error: true,
        };
        setMessages((prev) => [...prev, errorMsg]);
        setError(msg);
      } finally {
        setLoading(false);
      }
    },
    [messages, loading]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return { messages, loading, error, sendMessage, clearMessages };
}
