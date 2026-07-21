import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type HeadingProps = HTMLAttributes<HTMLHeadingElement> & {
  as?: "h1" | "h2" | "h3" | "h4";
  size?: "sm" | "md" | "lg" | "xl";
};

const sizes = {
  lg: "text-2xl",
  md: "text-xl",
  sm: "text-base",
  xl: "text-3xl",
};

function Heading({ as: Component = "h2", className, size = "md", ...props }: HeadingProps) {
  return (
    <Component
      className={cn("font-semibold tracking-normal text-foreground", sizes[size], className)}
      {...props}
    />
  );
}

export { Heading };
export type { HeadingProps };
