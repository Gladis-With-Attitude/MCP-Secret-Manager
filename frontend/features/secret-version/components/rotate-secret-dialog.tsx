"use client";

import { Dialog } from "@/components/overlay/dialog";

import type { SecretVersionFormValues } from "../types/secret-version";
import { SecretVersionForm } from "./secret-version-form";

type RotateSecretDialogProps = {
  error?: string | null;
  isOpen: boolean;
  isSubmitting?: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (values: SecretVersionFormValues) => void | Promise<void>;
  secretName?: string | null;
};

function RotateSecretDialog({
  error,
  isOpen,
  isSubmitting = false,
  onOpenChange,
  onSubmit,
  secretName,
}: RotateSecretDialogProps) {
  return (
    <Dialog
      description="Create an immutable secret version. Encryption remains fully backend-owned."
      onOpenChange={onOpenChange}
      open={isOpen}
      title="Rotate secret"
    >
      <SecretVersionForm
        error={error}
        isSubmitting={isSubmitting}
        onCancel={() => onOpenChange(false)}
        onSubmit={onSubmit}
        secretName={secretName}
        submitLabel="Create version"
      />
    </Dialog>
  );
}

export { RotateSecretDialog };
export type { RotateSecretDialogProps };
