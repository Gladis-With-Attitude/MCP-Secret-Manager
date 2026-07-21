import { Circle } from "lucide-react";

import { cn } from "@/lib/utils";

type SidebarFooterProps = {
  isCollapsed?: boolean;
};

function SidebarFooter({ isCollapsed = false }: SidebarFooterProps) {
  return (
    <div className="border-t border-border p-3">
      <div className="flex items-center gap-2 rounded-md border border-border px-2 py-2 text-xs text-muted-foreground">
        <Circle aria-hidden="true" className="size-2 fill-emerald-500 text-emerald-500" />
        <span className={cn(isCollapsed && "sr-only")}>System ready</span>
      </div>
    </div>
  );
}

export { SidebarFooter };
export type { SidebarFooterProps };
