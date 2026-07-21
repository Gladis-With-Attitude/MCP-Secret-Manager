"use client";

import * as DialogPrimitive from "@radix-ui/react-dialog";
import type { ReactNode } from "react";

import { Button } from "@/components/buttons/button";
import { cn } from "@/lib/utils";

type ConfirmDialogProps = {
  cancelLabel?: string;
  className?: string;
  confirmLabel?: string;
  defaultOpen?: boolean;
  description: ReactNode;
  isConfirming?: boolean;
  onConfirm: () => void;
  onOpenChange?: (open: boolean) => void;
  open?: boolean;
  title: ReactNode;
  trigger?: ReactNode;
  variant?: "default" | "danger";
};

function ConfirmDialog({
  cancelLabel = "Cancel",
  className,
  confirmLabel = "Confirm",
  defaultOpen,
  description,
  isConfirming = false,
  onConfirm,
  onOpenChange,
  open,
  title,
  trigger,
  variant = "default",
}: ConfirmDialogProps) {
  return (
    <DialogPrimitive.Root defaultOpen={defaultOpen} onOpenChange={onOpenChange} open={open}>
      {trigger ? <DialogPrimitive.Trigger asChild>{trigger}</DialogPrimitive.Trigger> : null}
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-black/50" />
        <DialogPrimitive.Content
          className={cn(
            "fixed left-1/2 top-1/2 z-50 grid w-[calc(100%-2rem)] max-w-md -translate-x-1/2 -translate-y-1/2 gap-5 rounded-lg border border-border bg-background p-6 text-foreground shadow-lg outline-none focus-visible:ring-2 focus-visible:ring-ring",
            className,
          )}
        >
          <div className="grid gap-2">
            <DialogPrimitive.Title className="text-lg font-semibold text-foreground">
              {title}
            </DialogPrimitive.Title>
            <DialogPrimitive.Description className="text-sm text-muted-foreground">
              {description}
            </DialogPrimitive.Description>
          </div>
          <div className="flex flex-wrap justify-end gap-2">
            <DialogPrimitive.Close asChild>
              <Button disabled={isConfirming} variant="outline">
                {cancelLabel}
              </Button>
            </DialogPrimitive.Close>
            <Button
              isLoading={isConfirming}
              onClick={onConfirm}
              variant={variant === "danger" ? "danger" : "primary"}
            >
              {confirmLabel}
            </Button>
          </div>
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  );
}

export { ConfirmDialog };
export type { ConfirmDialogProps };
