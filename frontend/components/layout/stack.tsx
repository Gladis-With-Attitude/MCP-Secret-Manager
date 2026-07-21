import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type StackProps = HTMLAttributes<HTMLDivElement> & {
  gap?: "xs" | "sm" | "md" | "lg" | "xl";
};

const gaps = {
  lg: "gap-6",
  md: "gap-4",
  sm: "gap-3",
  xl: "gap-8",
  xs: "gap-2",
};

function Stack({ className, gap = "md", ...props }: StackProps) {
  return <div className={cn("flex flex-col", gaps[gap], className)} {...props} />;
}

export { Stack };
export type { StackProps };
