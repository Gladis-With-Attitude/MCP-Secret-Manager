"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import type { Resolver } from "react-hook-form";
import { useForm } from "react-hook-form";

import { Button } from "@/components/buttons/button";
import { FormField } from "@/components/forms/form-field";
import { Input } from "@/components/forms/input";
import { Select } from "@/components/forms/select";
import { Dialog } from "@/components/overlay/dialog";

import type { Role, RoleAssignmentValues } from "../types/rbac";
import { roleAssignmentSchema, type RoleAssignmentSchemaValues } from "../validation/rbac-schema";

type AssignRoleDialogProps = {
  actorId?: string;
  error?: string | null;
  isOpen: boolean;
  isSubmitting?: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (values: RoleAssignmentValues) => void | Promise<void>;
  roles: Role[];
};

function AssignRoleDialog({
  actorId = "",
  error,
  isOpen,
  isSubmitting = false,
  onOpenChange,
  onSubmit,
  roles,
}: AssignRoleDialogProps) {
  const {
    formState: { errors },
    handleSubmit,
    register,
    reset,
    setValue,
    watch,
  } = useForm<RoleAssignmentSchemaValues>({
    defaultValues: {
      actorId,
      roleId: roles[0]?.id ?? "",
    },
    resolver: zodResolver(roleAssignmentSchema) as Resolver<RoleAssignmentSchemaValues>,
  });
  const selectedRoleId = watch("roleId");

  async function handleValidSubmit(values: RoleAssignmentSchemaValues) {
    await onSubmit({
      actorId: values.actorId.trim(),
      roleId: values.roleId,
    });
    reset({ actorId: values.actorId.trim(), roleId: roles[0]?.id ?? "" });
  }

  return (
    <Dialog
      description="Assign a backend role to an actor. Authorization is still validated by the backend."
      onOpenChange={onOpenChange}
      open={isOpen}
      title="Assign role"
    >
      <form
        className="grid gap-4"
        onSubmit={(event) => {
          void handleSubmit(handleValidSubmit)(event);
        }}
      >
        <FormField error={errors.actorId?.message} id="rbac-actor-id" label="Actor ID" required>
          <Input
            aria-invalid={Boolean(errors.actorId)}
            autoComplete="off"
            disabled={isSubmitting}
            id="rbac-actor-id"
            placeholder="actor-id"
            {...register("actorId")}
          />
        </FormField>
        <FormField error={errors.roleId?.message} id="rbac-assigned-role" label="Role" required>
          <Select
            disabled={isSubmitting || !roles.length}
            id="rbac-assigned-role"
            onValueChange={(value) => setValue("roleId", value, { shouldValidate: true })}
            options={roles.map((role) => ({ label: role.name, value: role.id }))}
            value={selectedRoleId}
          />
        </FormField>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        <div className="flex flex-wrap justify-end gap-2">
          <Button disabled={isSubmitting} onClick={() => onOpenChange(false)} variant="outline">
            Cancel
          </Button>
          <Button disabled={!roles.length} isLoading={isSubmitting} type="submit">
            Assign
          </Button>
        </div>
      </form>
    </Dialog>
  );
}

export { AssignRoleDialog };
export type { AssignRoleDialogProps };
