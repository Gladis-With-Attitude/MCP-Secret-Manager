import { ShieldAlert } from "lucide-react";
import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils";

type ForbiddenStateProps = HTMLAttributes<HTMLDivElement> & {
  action?: ReactNode;
  description?: ReactNode;
  title?: ReactNode;
};

function ForbiddenState({
  action,
  className,
  description = "You do not have access to this content.",
  title = "Access unavailable",
  ...props
}: ForbiddenStateProps) {
  return (
    <div
      className={cn(
        "flex min-h-40 flex-col items-center justify-center gap-3 rounded-lg border border-border bg-muted/20 p-6 text-center",
        className,
      )}
      role="status"
      {...props}
    >
      <ShieldAlert aria-hidden="true" className="size-6 text-muted-foreground" />
      <div>
        <p className="text-sm font-medium text-foreground">{title}</p>
        {description ? (
          <p className="mt-1 max-w-md text-sm text-muted-foreground">{description}</p>
        ) : null}
      </div>
      {action ? <div className="mt-1">{action}</div> : null}
    </div>
  );
}

export { ForbiddenState };
export type { ForbiddenStateProps };
