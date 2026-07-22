"use client";

import { Dialog } from "@/components/overlay/dialog";

import type { Secret, SecretFormValues } from "../types/secret";
import { SecretForm } from "./secret-form";

type SecretDialogProps = {
  error?: string | null;
  includeValue?: boolean;
  isOpen: boolean;
  isSubmitting?: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (values: SecretFormValues) => void | Promise<void>;
  projectName?: string | null;
  secret?: Secret;
  submitLabel: string;
  title: string;
};

function SecretDialog({
  error,
  includeValue,
  isOpen,
  isSubmitting,
  onOpenChange,
  onSubmit,
  projectName,
  secret,
  submitLabel,
  title,
}: SecretDialogProps) {
  return (
    <Dialog
      description="Secret values are sensitive and must never be placed in metadata."
      onOpenChange={onOpenChange}
      open={isOpen}
      title={title}
    >
      <SecretForm
        error={error}
        includeValue={includeValue}
        isSubmitting={isSubmitting}
        onCancel={() => onOpenChange(false)}
        onSubmit={onSubmit}
        projectName={projectName}
        secret={secret}
        submitLabel={submitLabel}
      />
    </Dialog>
  );
}

export { SecretDialog };
export type { SecretDialogProps };
