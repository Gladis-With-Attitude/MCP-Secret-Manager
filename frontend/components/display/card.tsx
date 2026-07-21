import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type CardProps = HTMLAttributes<HTMLDivElement> & {
  variant?: "default" | "summary" | "settings" | "empty" | "security";
};

const variants = {
  default: "bg-card",
  empty: "bg-muted/30",
  security: "border-sky-500/25 bg-card",
  settings: "bg-card",
  summary: "bg-card",
};

function Card({ className, variant = "default", ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-lg border border-border p-4 text-card-foreground",
        variants[variant],
        className,
      )}
      {...props}
    />
  );
}

export { Card };
export type { CardProps };
