"use client";

import { Dialog } from "@/components/overlay/dialog";

import type { Project, ProjectFormValues } from "../types/project";
import { ProjectForm } from "./project-form";

type ProjectDialogProps = {
  error?: string | null;
  isOpen: boolean;
  isSubmitting?: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (values: ProjectFormValues) => void | Promise<void>;
  project?: Project;
  submitLabel: string;
  title: string;
  vaultName?: string | null;
};

function ProjectDialog({
  error,
  isOpen,
  isSubmitting,
  onOpenChange,
  onSubmit,
  project,
  submitLabel,
  title,
  vaultName,
}: ProjectDialogProps) {
  return (
    <Dialog
      description="Project metadata must stay non-sensitive and inside the selected vault."
      onOpenChange={onOpenChange}
      open={isOpen}
      title={title}
    >
      <ProjectForm
        error={error}
        isSubmitting={isSubmitting}
        onCancel={() => onOpenChange(false)}
        onSubmit={onSubmit}
        project={project}
        submitLabel={submitLabel}
        vaultName={vaultName}
      />
    </Dialog>
  );
}

export { ProjectDialog };
export type { ProjectDialogProps };
