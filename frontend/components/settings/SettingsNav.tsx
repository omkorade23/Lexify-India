"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Palette, Brain, FileText, User } from "lucide-react";

const SETTINGS_NAV = [
  { href: "/settings/appearance", label: "Appearance", icon: Palette },
  { href: "/settings/ai", label: "AI Preferences", icon: Brain },
  { href: "/settings/documents", label: "Documents", icon: FileText },
  { href: "/settings/account", label: "Account", icon: User },
];

export default function SettingsNav() {
  const pathname = usePathname();

  return (
    <nav className="space-y-0.5" aria-label="Settings navigation">
      {SETTINGS_NAV.map(({ href, label, icon: Icon }) => {
        const active = pathname === href || pathname.startsWith(href + "/");
        return (
          <Link
            key={href}
            href={href}
            aria-label={label}
            aria-current={active ? "page" : undefined}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2.5 text-[13px] font-medium transition-all duration-150",
              active
                ? "bg-bg-elevated text-text-primary border-l-[2px] border-accent pl-[10px]"
                : "text-text-secondary hover:bg-white/[0.04] hover:text-text-body"
            )}
          >
            <Icon size={15} className="shrink-0" />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
