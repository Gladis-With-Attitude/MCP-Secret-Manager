"use client";

import { useId } from "react";

import * as CheckboxPrimitive from "@radix-ui/react-checkbox";
import { Check } from "lucide-react";
import type { ComponentPropsWithoutRef } from "react";

import { cn } from "@/lib/utils";

type CheckboxProps = ComponentPropsWithoutRef<typeof CheckboxPrimitive.Root> & {
  label?: string;
};

function Checkbox({ className, id, label, ...props }: CheckboxProps) {
  const generatedId = useId();
  const checkboxId = id ?? generatedId;

  return (
    <div className={cn("inline-flex items-center gap-2", !label && "gap-0")}>
      <CheckboxPrimitive.Root
        className={cn(
          "peer flex size-4 shrink-0 items-center justify-center rounded border border-input bg-background shadow-sm outline-none transition-colors focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:border-primary data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground",
          className,
        )}
        id={checkboxId}
        {...props}
      >
        <CheckboxPrimitive.Indicator>
          <Check aria-hidden="true" className="size-3" />
        </CheckboxPrimitive.Indicator>
      </CheckboxPrimitive.Root>
      {label ? (
        <label className="text-sm text-foreground" htmlFor={checkboxId}>
          {label}
        </label>
      ) : null}
    </div>
  );
}

export { Checkbox };
export type { CheckboxProps };
