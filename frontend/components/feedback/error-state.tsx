import { AlertTriangle } from "lucide-react";
import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils";

type ErrorStateProps = HTMLAttributes<HTMLDivElement> & {
  action?: ReactNode;
  description?: ReactNode;
  title?: ReactNode;
};

function ErrorState({
  action,
  className,
  description,
  title = "Something went wrong",
  ...props
}: ErrorStateProps) {
  return (
    <div
      className={cn(
        "flex min-h-40 flex-col items-center justify-center gap-3 rounded-lg border border-destructive/30 bg-destructive/5 p-6 text-center",
        className,
      )}
      role="alert"
      {...props}
    >
      <AlertTriangle aria-hidden="true" className="size-6 text-destructive" />
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

export { ErrorState };
export type { ErrorStateProps };
