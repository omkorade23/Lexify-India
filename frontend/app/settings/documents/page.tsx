"use client";

import React, { useState } from "react";
import AppShell from "@/components/layout/AppShell";
import SettingsNav from "@/components/settings/SettingsNav";
import ToggleRow from "@/components/settings/ToggleRow";

export default function DocumentsSettingsPage() {
  const [autoProcess, setAutoProcess] = useState(true);
  const [ocrFallback, setOcrFallback] = useState(true);

  return (
    <AppShell>
      <div className="flex-1 overflow-y-auto">
        <div className="ambient-glow min-h-full px-8 py-8 max-w-[1200px]">
          <div className="flex gap-8">
            <aside className="w-48 shrink-0 hidden md:block" aria-label="Settings navigation">
              <SettingsNav />
            </aside>

            <main className="flex-1 min-w-0 space-y-8">
              <div>
                <h1 className="text-text-primary text-xl font-bold mb-1">Documents</h1>
                <p className="text-text-secondary text-sm">
                  Manage document processing preferences
                </p>
              </div>

              <section className="bg-bg-surface border border-border-default rounded-2xl p-6" aria-label="Processing settings">
                <h2 className="text-text-primary font-semibold text-sm mb-4">Processing</h2>
                <ToggleRow
                  label="Auto-process on Upload"
                  description="Begin OCR and embedding immediately after upload"
                  checked={autoProcess}
                  onChange={setAutoProcess}
                />
                <ToggleRow
                  label="OCR Fallback"
                  description="Use image OCR when PDF text extraction fails"
                  checked={ocrFallback}
                  onChange={setOcrFallback}
                />
              </section>

              <section className="bg-bg-surface border border-border-default rounded-2xl p-6" aria-label="Upload limits">
                <h2 className="text-text-primary font-semibold text-sm mb-4">Upload Limits</h2>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { label: "Max File Size", value: "10 MB" },
                    { label: "Max Pages", value: "Unlimited" },
                    { label: "Supported Formats", value: "PDF, JPG, PNG" },
                    { label: "Chunk Size", value: "800 tokens" },
                  ].map(({ label, value }) => (
                    <div key={label} className="bg-bg-elevated rounded-xl p-3">
                      <p className="text-text-muted text-[11px] uppercase tracking-wide mb-1">{label}</p>
                      <p className="text-text-primary text-[13px] font-semibold">{value}</p>
                    </div>
                  ))}
                </div>
              </section>
            </main>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
