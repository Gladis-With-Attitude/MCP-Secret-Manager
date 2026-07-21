"use client";

import { useEffect, useRef, useState } from "react";

import { usePathname } from "next/navigation";

import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

type MainLayoutProps = {
  children: ReactNode;
  className?: string;
};

function MainLayout({ children, className }: MainLayoutProps) {
  const pathname = usePathname();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const mobilePanelRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  const closeMobileNavigation = () => {
    setIsMobileOpen(false);
    previousFocusRef.current?.focus();
  };

  const openMobileNavigation = () => {
    previousFocusRef.current =
      document.activeElement instanceof HTMLElement ? document.activeElement : null;
    setIsMobileOpen(true);
  };

  useEffect(() => {
    if (!isMobileOpen) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        closeMobileNavigation();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    mobilePanelRef.current?.querySelector<HTMLElement>("a, button")?.focus();

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isMobileOpen]);

  return (
    <div className={cn("min-h-screen bg-background text-foreground", className)}>
      <div className="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:z-40 lg:block">
        <Sidebar isCollapsed={isSidebarCollapsed} pathname={pathname} />
      </div>

      {isMobileOpen ? (
        <div aria-modal="true" className="fixed inset-0 z-50 lg:hidden" role="dialog">
          <button
            aria-label="Close navigation"
            className="absolute inset-0 bg-black/50"
            onClick={closeMobileNavigation}
            type="button"
          />
          <div className="absolute inset-y-0 left-0 w-72 max-w-[85vw]" ref={mobilePanelRef}>
            <Sidebar onNavigate={closeMobileNavigation} pathname={pathname} />
          </div>
        </div>
      ) : null}

      <div
        className={cn(
          "min-h-screen transition-[padding-left]",
          isSidebarCollapsed ? "lg:pl-16" : "lg:pl-64",
        )}
      >
        <Topbar
          isSidebarCollapsed={isSidebarCollapsed}
          onMobileOpen={openMobileNavigation}
          onSidebarToggle={() => setIsSidebarCollapsed((value) => !value)}
        />
        <div className="px-4 py-6 sm:px-6 lg:px-8">{children}</div>
      </div>
    </div>
  );
}

export { MainLayout };
export type { MainLayoutProps };
