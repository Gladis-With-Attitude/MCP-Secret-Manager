import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type PageProps = HTMLAttributes<HTMLElement>;

function Page({ className, ...props }: PageProps) {
  return (
    <main className={cn("min-h-screen bg-background py-8 text-foreground", className)} {...props} />
  );
}

export { Page };
export type { PageProps };
