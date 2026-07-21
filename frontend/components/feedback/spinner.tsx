import { Loader2 } from "lucide-react";
import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type SpinnerProps = HTMLAttributes<HTMLDivElement> & {
  label?: string;
  size?: "sm" | "md" | "lg";
};

const sizes = {
  lg: "size-6",
  md: "size-5",
  sm: "size-4",
};

function Spinner({ className, label = "Loading", size = "md", ...props }: SpinnerProps) {
  return (
    <div
      aria-label={label}
      className={cn("inline-flex items-center", className)}
      role="status"
      {...props}
    >
      <Loader2
        aria-hidden="true"
        className={cn("animate-spin text-muted-foreground", sizes[size])}
      />
      <span className="sr-only">{label}</span>
    </div>
  );
}

export { Spinner };
export type { SpinnerProps };
