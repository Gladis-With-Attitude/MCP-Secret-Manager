"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { Button } from "@/components/buttons/button";
import { FormField } from "@/components/forms/form-field";
import { Input } from "@/components/forms/input";
import { Textarea } from "@/components/forms/textarea";
import { Stack } from "@/components/layout/stack";

import type { Project, ProjectFormValues } from "../types/project";
import { projectFormSchema, type ProjectFormSchemaValues } from "../validation/project-schema";

type ProjectFormProps = {
  error?: string | null;
  isSubmitting?: boolean;
  onCancel?: () => void;
  onSubmit: (values: ProjectFormValues) => void | Promise<void>;
  project?: Project;
  submitLabel: string;
  vaultName?: string | null;
};

function ProjectForm({
  error,
  isSubmitting = false,
  onCancel,
  onSubmit,
  project,
  submitLabel,
  vaultName,
}: ProjectFormProps) {
  const {
    formState: { errors },
    handleSubmit,
    register,
  } = useForm<ProjectFormSchemaValues>({
    defaultValues: {
      description: project?.description ?? "",
      name: project?.name ?? "",
    },
    resolver: zodResolver(projectFormSchema),
  });

  return (
    <form
      className="w-full"
      onSubmit={(event) => {
        void handleSubmit(onSubmit)(event);
      }}
    >
      <Stack>
        <FormField
          description={
            vaultName
              ? `This project will belong to ${vaultName}.`
              : "This project is created inside the current vault context."
          }
          error={errors.name?.message}
          id="project-name"
          label="Name"
          required
        >
          <Input
            aria-invalid={Boolean(errors.name)}
            autoComplete="off"
            disabled={isSubmitting}
            id="project-name"
            placeholder="API"
            {...register("name")}
          />
        </FormField>
        <FormField
          description="Optional non-sensitive context for operators."
          error={errors.description?.message}
          id="project-description"
          label="Description"
        >
          <Textarea
            aria-invalid={Boolean(errors.description)}
            disabled={isSubmitting}
            id="project-description"
            placeholder="Short non-sensitive description"
            {...register("description")}
          />
        </FormField>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        <div className="flex flex-wrap justify-end gap-2">
          {onCancel ? (
            <Button disabled={isSubmitting} onClick={onCancel} variant="outline">
              Cancel
            </Button>
          ) : null}
          <Button isLoading={isSubmitting} type="submit">
            {submitLabel}
          </Button>
        </div>
      </Stack>
    </form>
  );
}

export { ProjectForm };
export type { ProjectFormProps };
