"use client";

import { ConfirmDialog } from "@/components/overlay/confirm-dialog";

import type { SecretVersion } from "../types/secret-version";

type RestoreVersionDialogProps = {
  isOpen: boolean;
  isSubmitting?: boolean;
  onConfirm: () => void;
  onOpenChange: (open: boolean) => void;
  version: SecretVersion | null;
};

function RestoreVersionDialog({
  isOpen,
  isSubmitting = false,
  onConfirm,
  onOpenChange,
  version,
}: RestoreVersionDialogProps) {
  return (
    <ConfirmDialog
      confirmLabel="Restore version"
      description={
        version
          ? `Restore version ${version.version} as the current version. The backend remains the authority for authorization and lifecycle rules.`
          : "Restore this version as current."
      }
      isConfirming={isSubmitting}
      onConfirm={onConfirm}
      onOpenChange={onOpenChange}
      open={isOpen}
      title="Restore secret version"
    />
  );
}

export { RestoreVersionDialog };
export type { RestoreVersionDialogProps };
