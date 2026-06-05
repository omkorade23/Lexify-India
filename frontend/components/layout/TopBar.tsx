"use client";

import React from "react";
import Link from "next/link";
import { Scale, Menu } from "lucide-react";
import { cn } from "@/lib/utils";

interface TopBarProps {
  title?: React.ReactNode;
  actions?: React.ReactNode;
  onHamburger?: () => void;
  className?: string;
}

export default function TopBar({
  title,
  actions,
  onHamburger,
  className,
}: TopBarProps) {
  return (
    <header
      className={cn(
        "flex items-center gap-4 px-6 py-4 border-b border-border-default bg-bg-base shrink-0",
        className
      )}
    >
      {/* Mobile hamburger */}
      {onHamburger && (
        <button
          className="md:hidden p-1.5 rounded-lg text-text-muted hover:text-text-body hover:bg-white/[0.04] transition-colors"
          onClick={onHamburger}
          aria-label="Open menu"
        >
          <Menu size={20} />
        </button>
      )}

      {/* Mobile logo — links to landing page */}
      <Link
        href="/"
        className="md:hidden flex items-center gap-2 mr-auto"
        aria-label="Lexify India home"
      >
        <div className="w-7 h-7 rounded-md bg-accent flex items-center justify-center">
          <Scale size={13} className="text-[#0A0A0A]" />
        </div>
        <span className="text-text-primary font-semibold text-sm">Lexify India</span>
      </Link>

      {/* Title area */}
      {title && <div className="flex-1 min-w-0">{title}</div>}

      {/* Actions */}
      {actions && <div className="flex items-center gap-2 ml-auto">{actions}</div>}
    </header>
  );
}
