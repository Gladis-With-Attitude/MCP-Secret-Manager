"use client";

import { Dialog } from "@/components/overlay/dialog";

import type { ApiKeyFormValues } from "../types/api-key";
import { ApiKeyForm } from "./api-key-form";

type CreateApiKeyDialogProps = {
  error?: string | null;
  isOpen: boolean;
  isSubmitting?: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (values: ApiKeyFormValues) => void | Promise<void>;
};

function CreateApiKeyDialog({
  error,
  isOpen,
  isSubmitting = false,
  onOpenChange,
  onSubmit,
}: CreateApiKeyDialogProps) {
  return (
    <Dialog
      description="Create an API key for a service, agent or integration. The generated key is shown only once."
      onOpenChange={onOpenChange}
      open={isOpen}
      title="Create API key"
    >
      <ApiKeyForm
        error={error}
        isSubmitting={isSubmitting}
        onCancel={() => onOpenChange(false)}
        onSubmit={onSubmit}
        submitLabel="Create API key"
      />
    </Dialog>
  );
}

export { CreateApiKeyDialog };
export type { CreateApiKeyDialogProps };
