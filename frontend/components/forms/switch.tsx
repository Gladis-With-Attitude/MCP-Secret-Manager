"use client";

import { useId } from "react";

import * as SwitchPrimitive from "@radix-ui/react-switch";
import type { ComponentPropsWithoutRef } from "react";

import { cn } from "@/lib/utils";

type SwitchProps = ComponentPropsWithoutRef<typeof SwitchPrimitive.Root> & {
  label?: string;
};

function Switch({ className, id, label, ...props }: SwitchProps) {
  const generatedId = useId();
  const switchId = id ?? generatedId;

  return (
    <div className={cn("inline-flex items-center gap-2", !label && "gap-0")}>
      <SwitchPrimitive.Root
        className={cn(
          "peer inline-flex h-6 w-10 shrink-0 cursor-pointer items-center rounded-full border border-transparent bg-input shadow-sm outline-none transition-colors focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-primary",
          className,
        )}
        id={switchId}
        {...props}
      >
        <SwitchPrimitive.Thumb className="pointer-events-none block size-5 rounded-full bg-background shadow transition-transform data-[state=checked]:translate-x-4 data-[state=unchecked]:translate-x-0" />
      </SwitchPrimitive.Root>
      {label ? (
        <label className="text-sm text-foreground" htmlFor={switchId}>
          {label}
        </label>
      ) : null}
    </div>
  );
}

export { Switch };
export type { SwitchProps };
