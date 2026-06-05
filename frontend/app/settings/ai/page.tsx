"use client";

import React, { useState } from "react";
import AppShell from "@/components/layout/AppShell";
import SettingsNav from "@/components/settings/SettingsNav";
import ToggleRow from "@/components/settings/ToggleRow";

export default function AISettingsPage() {
  const [citationsEnabled, setCitationsEnabled] = useState(true);
  const [legalContextEnabled, setLegalContextEnabled] = useState(true);
  const [streamingEnabled, setStreamingEnabled] = useState(false);
  const [verboseMode, setVerboseMode] = useState(false);

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
                <h1 className="text-text-primary text-xl font-bold mb-1">AI Preferences</h1>
                <p className="text-text-secondary text-sm">
                  Control how the AI analyzes your documents
                </p>
              </div>

              <section className="bg-bg-surface border border-border-default rounded-2xl p-6" aria-label="AI features">
                <h2 className="text-text-primary font-semibold text-sm mb-4">Response Settings</h2>
                <ToggleRow
                  label="Show Citations"
                  description="Display source references with every answer"
                  checked={citationsEnabled}
                  onChange={setCitationsEnabled}
                />
                <ToggleRow
                  label="Include Legal Context"
                  description="Supplement answers with Indian law references"
                  checked={legalContextEnabled}
                  onChange={setLegalContextEnabled}
                />
                <ToggleRow
                  label="Streaming Responses"
                  description="Show answers as they are generated (experimental)"
                  checked={streamingEnabled}
                  onChange={setStreamingEnabled}
                />
                <ToggleRow
                  label="Verbose Mode"
                  description="Show more detailed explanations and context"
                  checked={verboseMode}
                  onChange={setVerboseMode}
                />
              </section>

              <section className="bg-bg-surface border border-border-default rounded-2xl p-6" aria-label="Model info">
                <h2 className="text-text-primary font-semibold text-sm mb-4">Current Model</h2>
                <div className="flex items-center justify-between py-3">
                  <div>
                    <p className="text-text-primary text-[13px] font-medium">LLM</p>
                    <p className="text-text-muted text-[12px]">Response generation</p>
                  </div>
                  <span className="text-accent text-[12px] font-medium bg-[rgba(34,197,94,0.10)] px-2.5 py-1 rounded-full">
                    gemini-2.5-flash
                  </span>
                </div>
                <div className="border-t border-border-default" />
                <div className="flex items-center justify-between py-3">
                  <div>
                    <p className="text-text-primary text-[13px] font-medium">Embeddings</p>
                    <p className="text-text-muted text-[12px]">Semantic search</p>
                  </div>
                  <span className="text-accent text-[12px] font-medium bg-[rgba(34,197,94,0.10)] px-2.5 py-1 rounded-full">
                    gemini-embedding-001
                  </span>
                </div>
              </section>
            </main>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
