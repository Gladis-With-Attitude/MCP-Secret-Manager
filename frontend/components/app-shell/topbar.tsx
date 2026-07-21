"use client";

import { Menu } from "lucide-react";

import { IconButton } from "@/components/buttons/icon-button";
import { cn } from "@/lib/utils";

import { BreadcrumbBar } from "./breadcrumb-bar";
import { CommandPalette } from "./command-palette";
import { GlobalSearch } from "./global-search";
import { NotificationCenter } from "./notification-center";
import { SidebarCollapse } from "./sidebar-collapse";
import { UserMenu } from "./user-menu";

type TopbarProps = {
  className?: string;
  isSidebarCollapsed: boolean;
  onMobileOpen: () => void;
  onSidebarToggle: () => void;
};

function Topbar({ className, isSidebarCollapsed, onMobileOpen, onSidebarToggle }: TopbarProps) {
  return (
    <header
      className={cn(
        "sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-border bg-background/95 px-4 backdrop-blur",
        className,
      )}
    >
      <IconButton
        className="lg:hidden"
        icon={<Menu className="size-4" />}
        label="Open navigation"
        onClick={onMobileOpen}
        size="compact"
        variant="ghost"
      />
      <div className="hidden lg:block">
        <SidebarCollapse isCollapsed={isSidebarCollapsed} onToggle={onSidebarToggle} />
      </div>
      <div className="min-w-0 flex-1">
        <BreadcrumbBar />
      </div>
      <div className="hidden items-center gap-2 md:flex">
        <GlobalSearch />
        <CommandPalette />
      </div>
      <NotificationCenter />
      <UserMenu />
    </header>
  );
}

export { Topbar };
export type { TopbarProps };
