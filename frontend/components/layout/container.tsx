import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type ContainerProps = HTMLAttributes<HTMLDivElement> & {
  size?: "sm" | "md" | "lg" | "xl" | "full";
};

const sizes = {
  full: "max-w-none",
  lg: "max-w-6xl",
  md: "max-w-4xl",
  sm: "max-w-2xl",
  xl: "max-w-7xl",
};

function Container({ className, size = "xl", ...props }: ContainerProps) {
  return (
    <div className={cn("mx-auto w-full px-4 sm:px-6 lg:px-8", sizes[size], className)} {...props} />
  );
}

export { Container };
export type { ContainerProps };
