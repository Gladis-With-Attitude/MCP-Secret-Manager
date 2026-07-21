"use client";

import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import type { ReactNode } from "react";

import { IconButton } from "@/components/buttons/icon-button";
import { cn } from "@/lib/utils";

type DialogProps = {
  children?: ReactNode;
  className?: string;
  closeLabel?: string;
  defaultOpen?: boolean;
  description?: ReactNode;
  footer?: ReactNode;
  onOpenChange?: (open: boolean) => void;
  open?: boolean;
  title: ReactNode;
  trigger?: ReactNode;
};

function Dialog({
  children,
  className,
  closeLabel = "Close dialog",
  defaultOpen,
  description,
  footer,
  onOpenChange,
  open,
  title,
  trigger,
}: DialogProps) {
  return (
    <DialogPrimitive.Root defaultOpen={defaultOpen} onOpenChange={onOpenChange} open={open}>
      {trigger ? <DialogPrimitive.Trigger asChild>{trigger}</DialogPrimitive.Trigger> : null}
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-black/50" />
        <DialogPrimitive.Content
          className={cn(
            "fixed left-1/2 top-1/2 z-50 grid w-[calc(100%-2rem)] max-w-lg -translate-x-1/2 -translate-y-1/2 gap-4 rounded-lg border border-border bg-background p-6 text-foreground shadow-lg outline-none focus-visible:ring-2 focus-visible:ring-ring",
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

export { Dialog };
export type { DialogProps };
