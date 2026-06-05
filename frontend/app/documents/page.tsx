"use client";

import React from "react";
import AppShell from "@/components/layout/AppShell";
import DocumentGrid from "@/components/documents/DocumentGrid";
import DocumentSearchBar from "@/components/documents/DocumentSearchBar";
import FilterChips from "@/components/documents/FilterChips";
import { useDocuments } from "@/hooks/useDocuments";
import Link from "next/link";
import { Upload } from "lucide-react";

export default function DocumentsPage() {
  const {
    filteredDocuments,
    searchQuery,
    activeFilter,
    filterOptions,
    setSearchQuery,
    setActiveFilter,
  } = useDocuments();

  return (
    <AppShell>
      <div className="flex-1 overflow-y-auto">
        <div className="ambient-glow min-h-full px-8 py-8 max-w-[1400px]">
          {/* Header */}
          <div className="flex items-start justify-between gap-4 mb-8">
            <div>
              <h1 className="text-text-primary text-2xl font-bold mb-1">
                My Documents
              </h1>
              <p className="text-text-secondary text-sm">
                {filteredDocuments.length === 0
                  ? "No documents yet"
                  : `${filteredDocuments.length} document${filteredDocuments.length !== 1 ? "s" : ""} in your library`}
              </p>
            </div>

            <Link
              href="/upload"
              className="flex items-center gap-2 bg-accent hover:bg-accent-hover text-[#0A0A0A] text-sm font-semibold px-4 py-2.5 rounded-xl transition-all duration-200 hover:shadow-accent-glow-sm shrink-0"
              aria-label="Upload new document"
            >
              <Upload size={15} />
              Upload New
            </Link>
          </div>

          {/* Search + filters */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-8">
            <DocumentSearchBar value={searchQuery} onChange={setSearchQuery} />
            <FilterChips
              filters={filterOptions}
              active={activeFilter}
              onSelect={setActiveFilter}
            />
          </div>

          {/* Grid */}
          <DocumentGrid documents={filteredDocuments} />

          {/* Load more (static — no pagination endpoint) */}
          {filteredDocuments.length > 8 && (
            <div className="mt-8 flex justify-center">
              <button className="px-6 py-2.5 rounded-xl text-text-secondary text-sm border border-white/[0.08] bg-white/[0.04] hover:bg-white/[0.06] transition-colors">
                Load More
              </button>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
