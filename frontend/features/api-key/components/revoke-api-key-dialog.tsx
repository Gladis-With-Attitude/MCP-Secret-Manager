"use client";

import { ConfirmDialog } from "@/components/overlay/confirm-dialog";

import type { ApiKey } from "../types/api-key";

type RevokeApiKeyDialogProps = {
  apiKey: ApiKey | null;
  isOpen: boolean;
  isSubmitting?: boolean;
  onConfirm: () => void;
  onOpenChange: (open: boolean) => void;
};

function RevokeApiKeyDialog({
  apiKey,
  isOpen,
  isSubmitting = false,
  onConfirm,
  onOpenChange,
}: RevokeApiKeyDialogProps) {
  return (
    <ConfirmDialog
      confirmLabel="Revoke API key"
      description={
        apiKey
          ? `Revoke ${apiKey.name}. Services, agents or integrations using this key may immediately fail.`
          : "Revoke this API key."
      }
      isConfirming={isSubmitting}
      onConfirm={onConfirm}
      onOpenChange={onOpenChange}
      open={isOpen}
      title="Revoke API key"
      variant="danger"
    />
  );
}

export { RevokeApiKeyDialog };
export type { RevokeApiKeyDialogProps };
