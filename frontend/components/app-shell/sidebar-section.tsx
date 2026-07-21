import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type SidebarSectionProps = {
  children: ReactNode;
  className?: string;
  isCollapsed?: boolean;
  label: string;
};

function SidebarSection({ children, className, isCollapsed = false, label }: SidebarSectionProps) {
  return (
    <section className={cn("grid gap-1", className)}>
      <h2
        className={cn(
          "px-3 text-xs font-medium uppercase text-muted-foreground",
          isCollapsed && "sr-only",
        )}
      >
        {label}
      </h2>
      <div className="grid gap-1">{children}</div>
    </section>
  );
}

export { SidebarSection };
export type { SidebarSectionProps };
