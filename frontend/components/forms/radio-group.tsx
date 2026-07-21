"use client";

import { useId } from "react";

import * as RadioGroupPrimitive from "@radix-ui/react-radio-group";
import type { ComponentPropsWithoutRef } from "react";

import { cn } from "@/lib/utils";

type RadioOption = {
  description?: string;
  disabled?: boolean;
  label: string;
  value: string;
};

type RadioGroupProps = ComponentPropsWithoutRef<typeof RadioGroupPrimitive.Root> & {
  options: RadioOption[];
};

function RadioGroup({ className, options, ...props }: RadioGroupProps) {
  const generatedId = useId();

  return (
    <RadioGroupPrimitive.Root className={cn("grid gap-3", className)} {...props}>
      {options.map((option, index) => {
        const itemId = `${generatedId}-${index}`;

        return (
          <div className="flex items-start gap-3 text-sm" key={option.value}>
            <RadioGroupPrimitive.Item
              className="mt-0.5 flex size-4 shrink-0 items-center justify-center rounded-full border border-input bg-background shadow-sm outline-none transition-colors focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:border-primary"
              disabled={option.disabled}
              id={itemId}
              value={option.value}
            >
              <RadioGroupPrimitive.Indicator className="size-2 rounded-full bg-primary" />
            </RadioGroupPrimitive.Item>
            <label htmlFor={itemId}>
              <span className="font-medium text-foreground">{option.label}</span>
              {option.description ? (
                <span className="block text-muted-foreground">{option.description}</span>
              ) : null}
            </label>
          </div>
        );
      })}
    </RadioGroupPrimitive.Root>
  );
}

export { RadioGroup };
export type { RadioGroupProps, RadioOption };
