"use client";

import { ConfirmDialog } from "@/components/overlay/confirm-dialog";

import type { Secret } from "../types/secret";

type DeleteSecretDialogProps = {
  isOpen: boolean;
  isSubmitting?: boolean;
  onConfirm: () => void;
  onOpenChange: (open: boolean) => void;
  secret: Secret;
};

function DeleteSecretDialog({
  isOpen,
  isSubmitting = false,
  onConfirm,
  onOpenChange,
  secret,
}: DeleteSecretDialogProps) {
  return (
    <ConfirmDialog
      confirmLabel="Archive secret"
      description={`Archive ${secret.name}. Secret values are not shown or included in this confirmation.`}
      isConfirming={isSubmitting}
      onConfirm={onConfirm}
      onOpenChange={onOpenChange}
      open={isOpen}
      title="Archive secret"
      variant="danger"
    />
  );
}

export { DeleteSecretDialog };
export type { DeleteSecretDialogProps };
