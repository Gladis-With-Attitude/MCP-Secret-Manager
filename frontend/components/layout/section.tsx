import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils";

type SectionProps = HTMLAttributes<HTMLElement> & {
  actions?: ReactNode;
  description?: ReactNode;
  title?: ReactNode;
  variant?: "default" | "dense" | "detail" | "form";
};

const variants = {
  default: "py-6",
  dense: "py-4",
  detail: "py-6",
  form: "py-6",
};

function Section({
  actions,
  children,
  className,
  description,
  title,
  variant = "default",
  ...props
}: SectionProps) {
  return (
    <section className={cn("w-full", variants[variant], className)} {...props}>
      {title || description || actions ? (
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            {title ? <h2 className="text-base font-semibold text-foreground">{title}</h2> : null}
            {description ? (
              <p className="mt-1 text-sm text-muted-foreground">{description}</p>
            ) : null}
          </div>
          {actions ? <div className="flex shrink-0 items-center gap-2">{actions}</div> : null}
        </div>
      ) : null}
      {children}
    </section>
  );
}

export { Section };
export type { SectionProps };
