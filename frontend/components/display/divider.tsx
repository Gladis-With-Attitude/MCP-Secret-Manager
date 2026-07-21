import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type DividerProps = HTMLAttributes<HTMLDivElement> & {
  orientation?: "horizontal" | "vertical";
  variant?: "default" | "subtle" | "section";
};

function Divider({
  className,
  orientation = "horizontal",
  variant = "default",
  ...props
}: DividerProps) {
  return (
    <div
      aria-orientation={orientation}
      className={cn(
        "shrink-0 bg-border",
        orientation === "horizontal" ? "h-px w-full" : "h-full min-h-6 w-px",
        variant === "subtle" && "opacity-60",
        variant === "section" && "my-6",
        className,
      )}
      role="separator"
      {...props}
    />
  );
}

export { Divider };
export type { DividerProps };
