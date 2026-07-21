"use client";

import { ConfirmDialog } from "@/components/overlay/confirm-dialog";

import type { Vault } from "../types/vault";

type DeleteVaultDialogProps = {
  isOpen: boolean;
  isSubmitting?: boolean;
  onConfirm: () => void;
  onOpenChange: (open: boolean) => void;
  vault: Vault;
};

function DeleteVaultDialog({
  isOpen,
  isSubmitting = false,
  onConfirm,
  onOpenChange,
  vault,
}: DeleteVaultDialogProps) {
  return (
    <ConfirmDialog
      confirmLabel="Archive vault"
      description={`Archive ${vault.name}. The backend remains authoritative for the final effect on related resources.`}
      isConfirming={isSubmitting}
      onConfirm={onConfirm}
      onOpenChange={onOpenChange}
      open={isOpen}
      title="Archive vault"
      variant="danger"
    />
  );
}

export { DeleteVaultDialog };
export type { DeleteVaultDialogProps };
