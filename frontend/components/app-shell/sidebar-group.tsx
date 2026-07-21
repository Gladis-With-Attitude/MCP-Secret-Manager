import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type SidebarGroupProps = {
  children: ReactNode;
  className?: string;
};

function SidebarGroup({ children, className }: SidebarGroupProps) {
  return <div className={cn("grid gap-4", className)}>{children}</div>;
}

export { SidebarGroup };
export type { SidebarGroupProps };
