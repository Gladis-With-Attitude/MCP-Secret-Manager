"use client";

import {
  Activity,
  Gauge,
  KeyRound,
  LockKeyhole,
  ScrollText,
  Settings,
  Shield,
  User,
  Workflow,
} from "lucide-react";

import { type NavigationItemId, navigationSections } from "@/config/navigation";
import { isActiveRoute, matchPathPattern } from "@/lib/navigation";
import { cn } from "@/lib/utils";

import { SidebarFooter } from "./sidebar-footer";
import { SidebarGroup } from "./sidebar-group";
import { SidebarHeader } from "./sidebar-header";
import { SidebarItem } from "./sidebar-item";
import { SidebarSection } from "./sidebar-section";

type SidebarProps = {
  className?: string;
  isCollapsed?: boolean;
  onNavigate?: () => void;
  pathname: string;
};

const navigationIcons = {
  "api-keys": KeyRound,
  audit: ScrollText,
  dashboard: Gauge,
  profile: User,
  projects: Workflow,
  rbac: Shield,
  secrets: LockKeyhole,
  settings: Settings,
  vaults: Activity,
} satisfies Record<NavigationItemId, typeof Gauge>;

function Sidebar({ className, isCollapsed = false, onNavigate, pathname }: SidebarProps) {
  const explicitActiveItemId = navigationSections
    .flatMap((section) => section.items)
    .flatMap(
      (item) =>
        item.activePathPatterns
          ?.filter((pattern) => matchPathPattern(pathname, pattern))
          .map((pattern) => ({ item, specificity: pattern.split("/").filter(Boolean).length })) ??
        [],
    )
    .sort((first, second) => second.specificity - first.specificity)[0]?.item.id;

  return (
    <aside
      className={cn(
        "flex h-full flex-col border-r border-border bg-background text-foreground",
        isCollapsed ? "w-16" : "w-64",
        className,
      )}
    >
      <SidebarHeader isCollapsed={isCollapsed} />
      <nav aria-label="Primary navigation" className="min-h-0 flex-1 overflow-y-auto p-3">
        <SidebarGroup>
          {navigationSections.map((section) => (
            <SidebarSection isCollapsed={isCollapsed} key={section.id} label={section.label}>
              {section.items.map((item) => (
                <SidebarItem
                  href={item.href}
                  icon={navigationIcons[item.id]}
                  isActive={
                    explicitActiveItemId
                      ? explicitActiveItemId === item.id
                      : isActiveRoute(pathname, item.href, item.activePathPatterns)
                  }
                  isCollapsed={isCollapsed}
                  key={item.id}
                  label={item.label}
                  onNavigate={onNavigate}
                />
              ))}
            </SidebarSection>
          ))}
        </SidebarGroup>
      </nav>
      <SidebarFooter isCollapsed={isCollapsed} />
    </aside>
  );
}

export { Sidebar };
export type { SidebarProps };
