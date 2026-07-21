import { ChevronRight } from "lucide-react";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type BreadcrumbItem = {
  href?: string;
  label: ReactNode;
};

type BreadcrumbProps = {
  className?: string;
  items: BreadcrumbItem[];
};

function Breadcrumb({ className, items }: BreadcrumbProps) {
  return (
    <nav aria-label="Breadcrumb" className={cn("text-sm", className)}>
      <ol className="flex min-w-0 flex-wrap items-center gap-1 text-muted-foreground">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;

          return (
            <li className="flex min-w-0 items-center gap-1" key={index}>
              {index > 0 ? <ChevronRight aria-hidden="true" className="size-4 shrink-0" /> : null}
              {item.href && !isLast ? (
                <a
                  className="truncate rounded-sm outline-none hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring"
                  href={item.href}
                >
                  {item.label}
                </a>
              ) : (
                <span
                  aria-current={isLast ? "page" : undefined}
                  className="truncate text-foreground"
                >
                  {item.label}
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

export { Breadcrumb };
export type { BreadcrumbItem, BreadcrumbProps };
