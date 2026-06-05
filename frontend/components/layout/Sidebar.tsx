"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  MessageSquare,
  FolderOpen,
  Upload,
  Settings,
  Search,
  Plus,
  Scale,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface NavItem {
  href: string;
  label: string;
  icon: React.ElementType;
  matchPrefix?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  { href: "/chat", label: "Chat", icon: MessageSquare, matchPrefix: true },
  { href: "/documents", label: "My Documents", icon: FolderOpen },
  { href: "/upload", label: "Upload Document", icon: Upload },
];

const BOTTOM_ITEMS: NavItem[] = [
  { href: "/settings", label: "Settings", icon: Settings },
];

interface SidebarProps {
  collapsed?: boolean;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
  className?: string;
}

export default function Sidebar({
  collapsed = false,
  onMouseEnter,
  onMouseLeave,
  className,
}: SidebarProps) {
  const pathname = usePathname();
  const [searchValue, setSearchValue] = useState("");

  const isActive = (item: NavItem) => {
    if (item.matchPrefix) {
      return pathname === item.href || pathname.startsWith(item.href + "/");
    }
    return pathname === item.href || pathname.startsWith(item.href + "/");
  };

  return (
    <aside
      className={cn(
        "flex flex-col h-full bg-bg-sidebar border-r border-border-default transition-all duration-300 overflow-hidden",
        className
      )}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      aria-label="Primary navigation"
    >
      {/* ── Logo (links to landing page) ──────────────────────────── */}
      <Link
        href="/"
        className="px-5 pt-6 pb-5 flex items-center gap-3 shrink-0 hover:opacity-80 transition-opacity"
        aria-label="Lexify India home"
      >
        <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center shrink-0">
          <Scale size={16} className="text-[#0A0A0A]" />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <p className="text-text-primary font-semibold text-[15px] leading-none">
              Lexify India
            </p>
            <p className="text-text-muted text-[11px] mt-0.5 leading-none">
              Legal Intelligence
            </p>
          </div>
        )}
      </Link>

      {/* ── New Chat button ────────────────────────────────────────── */}
      <div className={cn("px-3 mb-4 shrink-0", collapsed && "px-2")}>
        <Link
          href="/chat"
          className={cn(
            "flex items-center gap-2.5 w-full bg-accent hover:bg-accent-hover text-[#0A0A0A] font-semibold text-sm rounded-lg transition-all duration-200",
            collapsed ? "justify-center p-2.5" : "px-4 py-2.5",
            "hover:shadow-accent-glow-sm"
          )}
          aria-label="Start new chat"
        >
          <Plus size={16} />
          {!collapsed && <span>New Chat</span>}
        </Link>
      </div>

      {/* ── Search ────────────────────────────────────────────────── */}
      {!collapsed && (
        <div className="px-3 mb-5 shrink-0">
          <div className="relative">
            <Search
              size={13}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-text-placeholder"
            />
            <input
              type="text"
              placeholder="Search documents..."
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              className="w-full bg-bg-surface border border-border-default rounded-lg pl-8 pr-3 py-2 text-[13px] text-text-body placeholder:text-text-placeholder focus:border-accent focus:outline-none transition-colors"
              aria-label="Search documents"
            />
          </div>
        </div>
      )}

      {/* ── Nav section label ─────────────────────────────────────── */}
      {!collapsed && (
        <p className="label-caps px-5 mb-2 shrink-0">Navigation</p>
      )}

      {/* ── Main nav ─────────────────────────────────────────────── */}
      <nav className="flex-1 px-2 space-y-0.5 overflow-y-auto min-h-0">
        {NAV_ITEMS.map((item) => {
          const { href, label, icon: Icon } = item;
          const active = isActive(item);
          return (
            <Link
              key={href}
              href={href}
              aria-label={label}
              aria-current={active ? "page" : undefined}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-[13px] font-medium transition-all duration-150 relative",
                active
                  ? "bg-bg-elevated text-text-primary border-l-[2px] border-accent pl-[10px]"
                  : "text-text-secondary hover:bg-white/[0.04] hover:text-text-body",
                collapsed && "justify-center px-2"
              )}
            >
              <Icon size={16} className="shrink-0" />
              {!collapsed && <span>{label}</span>}
              {!collapsed && active && (
                <ChevronRight size={12} className="ml-auto text-accent" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* ── Separator ─────────────────────────────────────────────── */}
      <div className="mx-3 my-3 border-t border-border-default shrink-0" />

      {/* ── Bottom items ──────────────────────────────────────────── */}
      <div className="px-2 pb-4 space-y-0.5 shrink-0">
        {BOTTOM_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              aria-label={label}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-[13px] font-medium transition-all duration-150",
                active
                  ? "bg-bg-elevated text-text-primary border-l-[2px] border-accent pl-[10px]"
                  : "text-text-muted hover:bg-white/[0.04] hover:text-text-secondary",
                collapsed && "justify-center px-2"
              )}
            >
              <Icon size={16} className="shrink-0" />
              {!collapsed && <span>{label}</span>}
            </Link>
          );
        })}

        {/* Brand footer line */}
        {!collapsed && (
          <p
            className="px-3 pt-2 text-[12px]"
            style={{ color: "#666666" }}
          >
            Lexify India · Legal Intelligence
          </p>
        )}
      </div>
    </aside>
  );
}
