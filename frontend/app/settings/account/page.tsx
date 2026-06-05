"use client";

import React, { useState } from "react";
import AppShell from "@/components/layout/AppShell";
import SettingsNav from "@/components/settings/SettingsNav";
import { clearDocuments } from "@/lib/utils";
import { Trash2, AlertTriangle } from "lucide-react";

export default function AccountSettingsPage() {
  const [cleared, setCleared] = useState(false);

  const handleClear = () => {
    clearDocuments();
    setCleared(true);
  };

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
                <h1 className="text-text-primary text-xl font-bold mb-1">Account</h1>
                <p className="text-text-secondary text-sm">
                  Manage your data and session preferences
                </p>
              </div>

              {/* Data management */}
              <section className="bg-bg-surface border border-border-default rounded-2xl p-6" aria-label="Data management">
                <h2 className="text-text-primary font-semibold text-sm mb-2">Data Management</h2>
                <p className="text-text-muted text-[12px] mb-5">
                  Document registry is stored locally in your browser. Clearing it will remove all document history from this device.
                </p>

                {cleared ? (
                  <div className="flex items-center gap-2 text-accent text-[13px]">
                    <span className="w-5 h-5 rounded-full bg-[rgba(34,197,94,0.12)] flex items-center justify-center">
                      <span className="text-[10px]">✓</span>
                    </span>
                    Document registry cleared successfully
                  </div>
                ) : (
                  <button
                    onClick={handleClear}
                    className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-danger/30 bg-danger/10 text-danger text-[13px] font-medium hover:bg-danger/20 transition-colors"
                    aria-label="Clear document history"
                  >
                    <Trash2 size={14} />
                    Clear Document History
                  </button>
                )}
              </section>

              {/* App info */}
              <section className="bg-bg-surface border border-border-default rounded-2xl p-6" aria-label="Application information">
                <h2 className="text-text-primary font-semibold text-sm mb-4">Application Info</h2>
                <div className="space-y-2">
                  {[
                    { label: "Version", value: "1.0.0" },
                    { label: "Backend", value: "FastAPI + ChromaDB" },
                    { label: "AI Models", value: "Gemini 2.5 Flash" },
                    { label: "Knowledge Base", value: "37 Indian Law entries" },
                  ].map(({ label, value }) => (
                    <div key={label} className="flex items-center justify-between py-2 border-b border-border-default last:border-b-0">
                      <span className="text-text-secondary text-[13px]">{label}</span>
                      <span className="text-text-primary text-[13px] font-medium">{value}</span>
                    </div>
                  ))}
                </div>
              </section>

              {/* Warning */}
              <div className="flex items-start gap-3 px-4 py-3 rounded-xl border border-warning/20 bg-warning/5">
                <AlertTriangle size={16} className="text-warning shrink-0 mt-0.5" />
                <p className="text-warning/80 text-[12px] leading-relaxed">
                  Lexify India is a hackathon prototype. Do not use it for critical legal decisions without consulting a qualified lawyer.
                </p>
              </div>
            </main>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
