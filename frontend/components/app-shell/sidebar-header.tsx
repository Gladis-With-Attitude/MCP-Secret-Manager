import { ShieldCheck } from "lucide-react";

import { cn } from "@/lib/utils";

type SidebarHeaderProps = {
  isCollapsed?: boolean;
};

function SidebarHeader({ isCollapsed = false }: SidebarHeaderProps) {
  return (
    <div className="flex h-14 items-center gap-3 border-b border-border px-3">
      <div className="flex size-8 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground">
        <ShieldCheck aria-hidden="true" className="size-4" />
      </div>
      <div className={cn("min-w-0", isCollapsed && "sr-only")}>
        <p className="truncate text-sm font-semibold text-foreground">MCP Secret Manager</p>
        <p className="truncate text-xs text-muted-foreground">Administration console</p>
      </div>
    </div>
  );
}

export { SidebarHeader };
export type { SidebarHeaderProps };
