"use client";

import Link from "next/link";

import type { ComponentType } from "react";

import { cn } from "@/lib/utils";

type SidebarItemProps = {
  href: string;
  icon: ComponentType<{ className?: string }>;
  isActive?: boolean;
  isCollapsed?: boolean;
  label: string;
  onNavigate?: () => void;
};

function SidebarItem({
  href,
  icon: Icon,
  isActive = false,
  isCollapsed = false,
  label,
  onNavigate,
}: SidebarItemProps) {
  return (
    <Link
      aria-current={isActive ? "page" : undefined}
      className={cn(
        "flex h-9 items-center gap-3 rounded-md px-3 text-sm font-medium text-muted-foreground outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:ring-2 focus-visible:ring-ring",
        isActive && "bg-accent text-accent-foreground",
        isCollapsed && "justify-center px-0",
      )}
      href={href}
      onClick={onNavigate}
      title={isCollapsed ? label : undefined}
    >
      <Icon aria-hidden="true" className="size-4 shrink-0" />
      <span className={cn("truncate", isCollapsed && "sr-only")}>{label}</span>
    </Link>
  );
}

export { SidebarItem };
export type { SidebarItemProps };
