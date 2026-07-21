import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils";

type PageHeaderProps = HTMLAttributes<HTMLElement> & {
  actions?: ReactNode;
  badges?: ReactNode;
  breadcrumb?: ReactNode;
  description?: ReactNode;
  title: ReactNode;
};

function PageHeader({
  actions,
  badges,
  breadcrumb,
  className,
  description,
  title,
  ...props
}: PageHeaderProps) {
  return (
    <header className={cn("border-b border-border pb-6", className)} {...props}>
      {breadcrumb ? <div className="mb-4">{breadcrumb}</div> : null}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-2xl font-semibold tracking-normal text-foreground">{title}</h1>
            {badges}
          </div>
          {description ? (
            <p className="mt-2 max-w-3xl text-sm text-muted-foreground">{description}</p>
          ) : null}
        </div>
        {actions ? (
          <div className="flex shrink-0 flex-wrap items-center gap-2">{actions}</div>
        ) : null}
      </div>
    </header>
  );
}

export { PageHeader };
export type { PageHeaderProps };
