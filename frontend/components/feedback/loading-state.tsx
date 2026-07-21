import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils";

import { Spinner } from "./spinner";

type LoadingStateProps = HTMLAttributes<HTMLDivElement> & {
  description?: ReactNode;
  title?: ReactNode;
};

function LoadingState({ className, description, title = "Loading", ...props }: LoadingStateProps) {
  return (
    <div
      className={cn(
        "flex min-h-32 flex-col items-center justify-center gap-3 text-center",
        className,
      )}
      role="status"
      {...props}
    >
      <Spinner />
      <div>
        <p className="text-sm font-medium text-foreground">{title}</p>
        {description ? <p className="mt-1 text-sm text-muted-foreground">{description}</p> : null}
      </div>
    </div>
  );
}

export { LoadingState };
export type { LoadingStateProps };
