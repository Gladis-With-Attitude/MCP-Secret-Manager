"use client";

import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import type { ReactNode } from "react";

import { IconButton } from "@/components/buttons/icon-button";
import { cn } from "@/lib/utils";

type DrawerSide = "bottom" | "left" | "right";

type DrawerProps = {
  children?: ReactNode;
  className?: string;
  closeLabel?: string;
  defaultOpen?: boolean;
  description?: ReactNode;
  footer?: ReactNode;
  onOpenChange?: (open: boolean) => void;
  open?: boolean;
  side?: DrawerSide;
  title: ReactNode;
  trigger?: ReactNode;
};

const sideClassName: Record<DrawerSide, string> = {
  bottom: "inset-x-0 bottom-0 max-h-[85vh] rounded-t-lg border-t",
  left: "inset-y-0 left-0 h-full w-[min(24rem,calc(100%-2rem))] border-r",
  right: "inset-y-0 right-0 h-full w-[min(24rem,calc(100%-2rem))] border-l",
};

function Drawer({
  children,
  className,
  closeLabel = "Close drawer",
  defaultOpen,
  description,
  footer,
  onOpenChange,
  open,
  side = "right",
  title,
  trigger,
}: DrawerProps) {
  return (
    <DialogPrimitive.Root defaultOpen={defaultOpen} onOpenChange={onOpenChange} open={open}>
      {trigger ? <DialogPrimitive.Trigger asChild>{trigger}</DialogPrimitive.Trigger> : null}
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-black/50" />
        <DialogPrimitive.Content
          className={cn(
            "fixed z-50 grid gap-4 border-border bg-background p-6 text-foreground shadow-lg outline-none focus-visible:ring-2 focus-visible:ring-ring",
            sideClassName[side],
            className,
          )}
        >
          <div className="grid gap-2 pr-10">
            <DialogPrimitive.Title className="text-lg font-semibold text-foreground">
              {title}
            </DialogPrimitive.Title>
            {description ? (
              <DialogPrimitive.Description className="text-sm text-muted-foreground">
                {description}
              </DialogPrimitive.Description>
            ) : null}
          </div>
          {children ? <div className="text-sm text-foreground">{children}</div> : null}
          {footer ? <div className="flex flex-wrap justify-end gap-2">{footer}</div> : null}
          <DialogPrimitive.Close asChild>
            <IconButton
              className="absolute right-4 top-4"
              icon={<X className="size-4" />}
              label={closeLabel}
              size="compact"
              variant="ghost"
            />
          </DialogPrimitive.Close>
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
}

export { Drawer };
export type { DrawerProps, DrawerSide };
