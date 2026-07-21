import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type FieldErrorProps = HTMLAttributes<HTMLParagraphElement>;

function FieldError({ className, ...props }: FieldErrorProps) {
  return <p className={cn("text-sm text-destructive", className)} role="alert" {...props} />;
}

export { FieldError };
export type { FieldErrorProps };
