"use client";

import { Dialog } from "@/components/overlay/dialog";

import type { Vault, VaultFormValues } from "../types/vault";
import { VaultForm } from "./vault-form";

type VaultDialogProps = {
  error?: string | null;
  isOpen: boolean;
  isSubmitting?: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (values: VaultFormValues) => void | Promise<void>;
  submitLabel: string;
  title: string;
  vault?: Vault;
};

function VaultDialog({
  error,
  isOpen,
  isSubmitting,
  onOpenChange,
  onSubmit,
  submitLabel,
  title,
  vault,
}: VaultDialogProps) {
  return (
    <Dialog
      description="Vault metadata must stay non-sensitive."
      onOpenChange={onOpenChange}
      open={isOpen}
      title={title}
    >
      <VaultForm
        error={error}
        isSubmitting={isSubmitting}
        onCancel={() => onOpenChange(false)}
        onSubmit={onSubmit}
        submitLabel={submitLabel}
        vault={vault}
      />
    </Dialog>
  );
}

export { VaultDialog };
export type { VaultDialogProps };
