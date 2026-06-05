"use client";

import React from "react";
import { Search } from "lucide-react";

interface DocumentSearchBarProps {
  value: string;
  onChange: (v: string) => void;
}

export default function DocumentSearchBar({ value, onChange }: DocumentSearchBarProps) {
  return (
    <div className="relative">
      <Search
        size={15}
        className="absolute left-3.5 top-1/2 -translate-y-1/2 text-text-placeholder"
      />
      <input
        type="text"
        placeholder="Search documents..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full sm:w-72 bg-bg-surface border border-border-default rounded-xl pl-9 pr-4 py-2.5 text-sm text-text-body placeholder:text-text-placeholder focus:border-accent focus:outline-none transition-colors"
        aria-label="Search documents"
      />
    </div>
  );
}
