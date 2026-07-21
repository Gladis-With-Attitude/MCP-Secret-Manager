import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type TextProps = HTMLAttributes<HTMLParagraphElement> & {
  tone?: "default" | "muted" | "danger" | "success" | "warning";
  size?: "sm" | "md" | "lg";
};

const tones = {
  danger: "text-destructive",
  default: "text-foreground",
  muted: "text-muted-foreground",
  success: "text-emerald-700 dark:text-emerald-300",
  warning: "text-amber-700 dark:text-amber-300",
};

const sizes = {
  lg: "text-base",
  md: "text-sm",
  sm: "text-xs",
};

function Text({ className, size = "md", tone = "default", ...props }: TextProps) {
  return <p className={cn("leading-6", sizes[size], tones[tone], className)} {...props} />;
}

export { Text };
export type { TextProps };
