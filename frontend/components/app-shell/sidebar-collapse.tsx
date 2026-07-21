"use client";

import { PanelLeftClose, PanelLeftOpen } from "lucide-react";

import { IconButton } from "@/components/buttons/icon-button";

type SidebarCollapseProps = {
  isCollapsed: boolean;
  onToggle: () => void;
};

function SidebarCollapse({ isCollapsed, onToggle }: SidebarCollapseProps) {
  return (
    <IconButton
      icon={
        isCollapsed ? <PanelLeftOpen className="size-4" /> : <PanelLeftClose className="size-4" />
      }
      label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
      onClick={onToggle}
      size="compact"
      variant="toolbar"
    />
  );
}

export { SidebarCollapse };
export type { SidebarCollapseProps };
