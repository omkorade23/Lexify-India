"use client";

import React, { useState } from "react";
import AppShell from "@/components/layout/AppShell";
import SettingsNav from "@/components/settings/SettingsNav";
import TypographySlider from "@/components/settings/TypographySlider";
import ToggleRow from "@/components/settings/ToggleRow";

export default function AppearanceSettingsPage() {
  const [fontSize, setFontSize] = useState(14);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [highContrast, setHighContrast] = useState(false);

  return (
    <AppShell>
      <div className="flex-1 overflow-y-auto">
        <div className="ambient-glow min-h-full px-8 py-8 max-w-[1200px]">
          <div className="flex gap-8">
            {/* Settings nav */}
            <aside className="w-48 shrink-0 hidden md:block" aria-label="Settings navigation">
              <SettingsNav />
            </aside>

            {/* Content */}
            <main className="flex-1 min-w-0 space-y-8">
              <div>
                <h1 className="text-text-primary text-xl font-bold mb-1">Appearance</h1>
                <p className="text-text-secondary text-sm">
                  Customize how Lexify India looks and feels
                </p>
              </div>

              {/* Typography */}
              <section
                className="bg-bg-surface border border-border-default rounded-2xl p-6 space-y-4"
                aria-label="Typography settings"
              >
                <div>
                  <h2 className="text-text-primary font-semibold text-sm mb-1">Typography</h2>
                  <p className="text-text-muted text-[12px]">Adjust text size for reading comfort</p>
                </div>
                <TypographySlider value={fontSize} onChange={setFontSize} />
              </section>

              {/* Accessibility */}
              <section
                className="bg-bg-surface border border-border-default rounded-2xl p-6"
                aria-label="Accessibility settings"
              >
                <h2 className="text-text-primary font-semibold text-sm mb-4">Accessibility</h2>
                <ToggleRow
                  label="Reduce Motion"
                  description="Disable animations for a calmer experience"
                  checked={reducedMotion}
                  onChange={setReducedMotion}
                />
                <ToggleRow
                  label="High Contrast Mode"
                  description="Increase contrast for better readability"
                  checked={highContrast}
                  onChange={setHighContrast}
                />
              </section>
            </main>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
