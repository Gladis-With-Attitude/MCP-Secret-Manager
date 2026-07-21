"use client";

import { ConfirmDialog } from "@/components/overlay/confirm-dialog";

import type { Project } from "../types/project";

type DeleteProjectDialogProps = {
  isOpen: boolean;
  isSubmitting?: boolean;
  onConfirm: () => void;
  onOpenChange: (open: boolean) => void;
  project: Project;
};

function DeleteProjectDialog({
  isOpen,
  isSubmitting = false,
  onConfirm,
  onOpenChange,
  project,
}: DeleteProjectDialogProps) {
  return (
    <ConfirmDialog
      confirmLabel="Archive project"
      description={`Archive ${project.name}. The backend remains authoritative for the final effect on related secrets.`}
      isConfirming={isSubmitting}
      onConfirm={onConfirm}
      onOpenChange={onOpenChange}
      open={isOpen}
      title="Archive project"
      variant="danger"
    />
  );
}

export { DeleteProjectDialog };
export type { DeleteProjectDialogProps };
