"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessageSquare, FolderOpen, Upload, Settings, Menu } from "lucide-react";
import { cn } from "@/lib/utils";

interface BottomNavProps {
  onHamburger?: () => void;
}

const TABS = [
  { href: "/chat", label: "Chat", icon: MessageSquare, matchPrefix: true },
  { href: "/documents", label: "Docs", icon: FolderOpen },
  { href: "/upload", label: "Upload", icon: Upload },
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function BottomNav({ onHamburger }: BottomNavProps) {
  const pathname = usePathname();

  return (
    <nav
      className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-bg-sidebar border-t border-border-default flex items-center"
      style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
      aria-label="Mobile navigation"
    >
      {/* Hamburger for full sidebar */}
      {onHamburger && (
        <button
          onClick={onHamburger}
          className="flex flex-col items-center justify-center gap-1 py-3 px-3 text-text-muted"
          aria-label="Open menu"
        >
          <Menu size={20} />
          <span className="text-[10px]">Menu</span>
        </button>
      )}

      {TABS.map(({ href, label, icon: Icon, matchPrefix }) => {
        const active = matchPrefix
          ? pathname === href || pathname.startsWith(href + "/")
          : pathname === href || pathname.startsWith(href + "/");
        return (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex flex-col items-center justify-center gap-1 flex-1 py-3 transition-colors",
              active ? "text-accent" : "text-text-muted"
            )}
            aria-label={label}
            aria-current={active ? "page" : undefined}
          >
            <Icon size={20} />
            <span className="text-[10px]">{label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
