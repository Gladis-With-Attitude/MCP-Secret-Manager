import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

import { FieldError } from "./field-error";

type FormFieldProps = {
  children: ReactNode;
  className?: string;
  description?: ReactNode;
  error?: ReactNode;
  id?: string;
  label: ReactNode;
  required?: boolean;
};

function FormField({
  children,
  className,
  description,
  error,
  id,
  label,
  required,
}: FormFieldProps) {
  const descriptionId = id && description ? `${id}-description` : undefined;
  const errorId = id && error ? `${id}-error` : undefined;

  return (
    <div className={cn("grid gap-2", className)}>
      <label className="text-sm font-medium leading-none text-foreground" htmlFor={id}>
        {label}
        {required ? (
          <span aria-hidden="true" className="ml-1 text-destructive">
            *
          </span>
        ) : null}
      </label>
      {children}
      {description ? (
        <p className="text-sm text-muted-foreground" id={descriptionId}>
          {description}
        </p>
      ) : null}
      {error ? <FieldError id={errorId}>{error}</FieldError> : null}
    </div>
  );
}

export { FormField };
export type { FormFieldProps };
