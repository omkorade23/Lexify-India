"use client";

import { useState, useEffect, useCallback } from "react";
import { getStoredDocuments } from "@/lib/utils";
import type { StoredDocument } from "@/lib/types";

const FILTER_OPTIONS = ["All", "Rental Agreement", "Employment Contract", "NDA", "Property Deed", "Legal Notice"] as const;
export type FilterOption = (typeof FILTER_OPTIONS)[number];

interface UseDocumentsReturn {
  documents: StoredDocument[];
  filteredDocuments: StoredDocument[];
  searchQuery: string;
  activeFilter: FilterOption;
  filterOptions: typeof FILTER_OPTIONS;
  setSearchQuery: (q: string) => void;
  setActiveFilter: (f: FilterOption) => void;
  refresh: () => void;
}

export function useDocuments(): UseDocumentsReturn {
  const [documents, setDocuments] = useState<StoredDocument[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeFilter, setActiveFilter] = useState<FilterOption>("All");

  const refresh = useCallback(() => {
    setDocuments(getStoredDocuments());
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch =
      !searchQuery ||
      doc.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.document_type.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesFilter =
      activeFilter === "All" ||
      doc.document_type
        .replace(/_/g, " ")
        .toLowerCase() === activeFilter.toLowerCase();

    return matchesSearch && matchesFilter;
  });

  return {
    documents,
    filteredDocuments,
    searchQuery,
    activeFilter,
    filterOptions: FILTER_OPTIONS,
    setSearchQuery,
    setActiveFilter,
    refresh,
  };
}
