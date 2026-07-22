"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import type { Resolver } from "react-hook-form";
import { useForm } from "react-hook-form";

import { Button } from "@/components/buttons/button";
import { FormField } from "@/components/forms/form-field";
import { Input } from "@/components/forms/input";
import { Dialog } from "@/components/overlay/dialog";

import type { ChangePasswordValues } from "../types/profile";
import {
  changePasswordSchema,
  type ChangePasswordSchemaValues,
} from "../validation/profile-schema";

type ChangePasswordDialogProps = {
  error?: string | null;
  isOpen: boolean;
  isSubmitting?: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (values: ChangePasswordValues) => void | Promise<void>;
};

function ChangePasswordDialog({
  error,
  isOpen,
  isSubmitting = false,
  onOpenChange,
  onSubmit,
}: ChangePasswordDialogProps) {
  const {
    formState: { errors },
    handleSubmit,
    register,
    reset,
  } = useForm<ChangePasswordSchemaValues>({
    defaultValues: {
      currentPassword: "",
      newPassword: "",
    },
    resolver: zodResolver(changePasswordSchema) as Resolver<ChangePasswordSchemaValues>,
  });

  async function handleValidSubmit(values: ChangePasswordSchemaValues) {
    await onSubmit(values);
    reset();
  }

  return (
    <Dialog
      description="Password validation and rotation are performed by the backend. Password values are never displayed."
      onOpenChange={(open) => {
        if (!open) {
          reset();
        }
        onOpenChange(open);
      }}
      open={isOpen}
      title="Change password"
    >
      <form
        className="grid gap-4"
        onSubmit={(event) => {
          void handleSubmit(handleValidSubmit)(event);
        }}
      >
        <FormField
          error={errors.currentPassword?.message}
          id="current-password"
          label="Current password"
          required
        >
          <Input
            aria-invalid={Boolean(errors.currentPassword)}
            autoComplete="current-password"
            disabled={isSubmitting}
            id="current-password"
            type="password"
            {...register("currentPassword")}
          />
        </FormField>
        <FormField
          error={errors.newPassword?.message}
          id="new-password"
          label="New password"
          required
        >
          <Input
            aria-invalid={Boolean(errors.newPassword)}
            autoComplete="new-password"
            disabled={isSubmitting}
            id="new-password"
            type="password"
            {...register("newPassword")}
          />
        </FormField>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        <div className="flex flex-wrap justify-end gap-2">
          <Button disabled={isSubmitting} onClick={() => onOpenChange(false)} variant="outline">
            Cancel
          </Button>
          <Button isLoading={isSubmitting} type="submit" variant="danger">
            Change password
          </Button>
        </div>
      </form>
    </Dialog>
  );
}

export { ChangePasswordDialog };
export type { ChangePasswordDialogProps };
