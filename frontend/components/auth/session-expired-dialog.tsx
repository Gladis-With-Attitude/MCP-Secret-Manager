"use client";

import type { ReactNode } from "react";

import { Button } from "@/components/buttons/button";
import { Dialog } from "@/components/overlay/dialog";

type SessionExpiredDialogProps = {
  actionLabel?: ReactNode;
  description?: ReactNode;
  onAction?: () => void;
  onOpenChange?: (open: boolean) => void;
  open: boolean;
  title?: ReactNode;
};

function SessionExpiredDialog({
  actionLabel = "Continue",
  description = "Your session has expired. Protected data has been cleared from this browser state.",
  onAction,
  onOpenChange,
  open,
  title = "Session expired",
}: SessionExpiredDialogProps) {
  return (
    <Dialog
      description={description}
      footer={<Button onClick={onAction}>{actionLabel}</Button>}
      onOpenChange={onOpenChange}
      open={open}
      title={title}
    />
  );
}

export { SessionExpiredDialog };
export type { SessionExpiredDialogProps };
