"use client";

import React, { useState } from "react";
import Sidebar from "./Sidebar";
import BottomNav from "./BottomNav";
import MobileDrawer from "./MobileDrawer";

interface AppShellProps {
  children: React.ReactNode;
}

export default function AppShell({ children }: AppShellProps) {
  const [tabletExpanded, setTabletExpanded] = useState(false);
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

  return (
    <div className="flex h-screen bg-bg-base overflow-hidden">
      {/* ── Desktop sidebar (1280px+): always 268px ───────────────────── */}
      <div className="hidden xl:flex w-[268px] shrink-0 h-full">
        <Sidebar className="w-[268px]" />
      </div>

      {/* ── Tablet sidebar (768px–1279px): icon-rail or expanded overlay ─ */}
      <div
        className="hidden md:flex xl:hidden shrink-0 h-full relative z-30"
        style={{ width: tabletExpanded ? 240 : 64 }}
        onMouseEnter={() => setTabletExpanded(true)}
        onMouseLeave={() => setTabletExpanded(false)}
      >
        <Sidebar
          collapsed={!tabletExpanded}
          className={
            tabletExpanded
              ? "w-60 shadow-2xl absolute left-0 top-0 bottom-0 z-40"
              : "w-16"
          }
        />
      </div>

      {/* ── Main content ────────────────────────────────────────────────── */}
      <main className="flex-1 min-w-0 h-full overflow-hidden flex flex-col">
        {children}
      </main>

      {/* ── Mobile bottom nav ────────────────────────────────────────────── */}
      <BottomNav onHamburger={() => setMobileDrawerOpen(true)} />

      {/* ── Mobile drawer ───────────────────────────────────────────────── */}
      <MobileDrawer
        open={mobileDrawerOpen}
        onClose={() => setMobileDrawerOpen(false)}
      />
    </div>
  );
}
