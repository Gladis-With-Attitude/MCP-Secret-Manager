"use client";

import * as TabsPrimitive from "@radix-ui/react-tabs";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type TabItem = {
  content: ReactNode;
  disabled?: boolean;
  label: ReactNode;
  value: string;
};

type TabsProps = {
  className?: string;
  defaultValue?: string;
  items: TabItem[];
  onValueChange?: (value: string) => void;
  value?: string;
};

function Tabs({ className, defaultValue, items, onValueChange, value }: TabsProps) {
  return (
    <TabsPrimitive.Root
      className={cn("w-full", className)}
      defaultValue={defaultValue ?? items[0]?.value}
      onValueChange={onValueChange}
      value={value}
    >
      <TabsPrimitive.List className="inline-flex h-10 items-center rounded-md border border-border bg-muted/40 p-1">
        {items.map((item) => (
          <TabsPrimitive.Trigger
            className="inline-flex h-8 items-center justify-center rounded-sm px-3 text-sm font-medium text-muted-foreground outline-none transition-colors hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm"
            disabled={item.disabled}
            key={item.value}
            value={item.value}
          >
            {item.label}
          </TabsPrimitive.Trigger>
        ))}
      </TabsPrimitive.List>
      {items.map((item) => (
        <TabsPrimitive.Content
          className="mt-4 outline-none focus-visible:ring-2 focus-visible:ring-ring"
          key={item.value}
          value={item.value}
        >
          {item.content}
        </TabsPrimitive.Content>
      ))}
    </TabsPrimitive.Root>
  );
}

export { Tabs };
export type { TabItem, TabsProps };
