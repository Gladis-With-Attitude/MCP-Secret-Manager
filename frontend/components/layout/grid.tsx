import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type GridProps = HTMLAttributes<HTMLDivElement> & {
  columns?: 1 | 2 | 3 | 4;
  gap?: "sm" | "md" | "lg";
};

const columnsMap = {
  1: "grid-cols-1",
  2: "grid-cols-1 md:grid-cols-2",
  3: "grid-cols-1 md:grid-cols-2 xl:grid-cols-3",
  4: "grid-cols-1 sm:grid-cols-2 xl:grid-cols-4",
};

const gaps = {
  lg: "gap-6",
  md: "gap-4",
  sm: "gap-3",
};

function Grid({ className, columns = 2, gap = "md", ...props }: GridProps) {
  return <div className={cn("grid", columnsMap[columns], gaps[gap], className)} {...props} />;
}

export { Grid };
export type { GridProps };
