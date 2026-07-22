"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import type { Resolver } from "react-hook-form";
import { useForm } from "react-hook-form";

import { Button } from "@/components/buttons/button";
import { FormField } from "@/components/forms/form-field";
import { Input } from "@/components/forms/input";
import { Textarea } from "@/components/forms/textarea";
import { Stack } from "@/components/layout/stack";

import type { Permission, Role, RoleFormValues } from "../types/rbac";
import { roleFormSchema, type RoleFormSchemaValues } from "../validation/rbac-schema";
import { PermissionMatrix } from "./permission-matrix";

type RoleFormProps = {
  error?: string | null;
  isSubmitting?: boolean;
  onCancel?: () => void;
  onSubmit: (values: RoleFormValues) => void | Promise<void>;
  permissions: Permission[];
  role?: Role;
  submitLabel: string;
};

function mapSchemaValuesToRoleFormValues(values: RoleFormSchemaValues): RoleFormValues {
  return {
    description: values.description?.trim() || undefined,
    name: values.name.trim(),
    permissionIds: values.permissionIds,
  };
}

function RoleForm({
  error,
  isSubmitting = false,
  onCancel,
  onSubmit,
  permissions,
  role,
  submitLabel,
}: RoleFormProps) {
  const {
    formState: { errors },
    handleSubmit,
    register,
    setValue,
    watch,
  } = useForm<RoleFormSchemaValues>({
    defaultValues: {
      description: role?.description ?? "",
      name: role?.name ?? "",
      permissionIds: role?.permissionIds ?? [],
    },
    resolver: zodResolver(roleFormSchema) as Resolver<RoleFormSchemaValues>,
  });
  const selectedPermissionIds = watch("permissionIds");
  const isSystemRole = role?.kind === "system";

  const handleValidSubmit = async (values: RoleFormSchemaValues) => {
    await onSubmit(mapSchemaValuesToRoleFormValues(values));
  };

  function handlePermissionToggle(permissionId: string, checked: boolean) {
    const nextValue = checked
      ? Array.from(new Set([...selectedPermissionIds, permissionId]))
      : selectedPermissionIds.filter((id) => id !== permissionId);

    setValue("permissionIds", nextValue, { shouldDirty: true, shouldValidate: true });
  }

  return (
    <form
      className="w-full"
      onSubmit={(event) => {
        void handleSubmit(handleValidSubmit)(event);
      }}
    >
      <Stack>
        <FormField
          description="Use a stable backend role identifier."
          error={errors.name?.message}
          id="rbac-role-name"
          label="Role name"
          required
        >
          <Input
            aria-invalid={Boolean(errors.name)}
            autoComplete="off"
            disabled={isSubmitting || isSystemRole}
            id="rbac-role-name"
            placeholder="security-admin"
            {...register("name")}
          />
        </FormField>
        <FormField
          description="Optional non-sensitive explanation for administrators."
          error={errors.description?.message}
          id="rbac-role-description"
          label="Description"
        >
          <Textarea
            aria-invalid={Boolean(errors.description)}
            disabled={isSubmitting || isSystemRole}
            id="rbac-role-description"
            placeholder="Can administer roles and assignments"
            {...register("description")}
          />
        </FormField>
        <FormField
          description="Permissions are backend-defined. The backend validates the final authorization change."
          error={errors.permissionIds?.message}
          id="rbac-role-permissions"
          label="Permissions"
          required
        >
          <PermissionMatrix
            disabled={isSubmitting || isSystemRole}
            onPermissionToggle={handlePermissionToggle}
            permissions={permissions}
            selectedPermissionIds={selectedPermissionIds}
          />
        </FormField>
        {isSystemRole ? (
          <p className="text-sm text-muted-foreground">
            System roles are read-only unless the backend explicitly allows changes.
          </p>
        ) : null}
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        <div className="flex flex-wrap justify-end gap-2">
          {onCancel ? (
            <Button disabled={isSubmitting} onClick={onCancel} type="button" variant="outline">
              Cancel
            </Button>
          ) : null}
          <Button disabled={isSystemRole} isLoading={isSubmitting} type="submit">
            {submitLabel}
          </Button>
        </div>
      </Stack>
    </form>
  );
}

export { mapSchemaValuesToRoleFormValues, RoleForm };
export type { RoleFormProps };
