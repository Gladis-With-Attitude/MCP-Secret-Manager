"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import type { Resolver } from "react-hook-form";
import { useForm } from "react-hook-form";

import { Button } from "@/components/buttons/button";
import { FormField } from "@/components/forms/form-field";
import { Input } from "@/components/forms/input";
import { Select } from "@/components/forms/select";
import { Textarea } from "@/components/forms/textarea";
import { Stack } from "@/components/layout/stack";

import type { ApiKeyFormValues } from "../types/api-key";
import {
  apiKeyFormSchema,
  type ApiKeyFormSchemaValues,
  parseApiKeyItems,
} from "../validation/api-key-schema";

type ApiKeyFormProps = {
  error?: string | null;
  isSubmitting?: boolean;
  onCancel?: () => void;
  onSubmit: (values: ApiKeyFormValues) => void | Promise<void>;
  submitLabel: string;
};

const ownerTypeOptions = [
  { label: "Service account", value: "service_account" },
  { label: "User", value: "user" },
];

function mapSchemaValuesToApiKeyFormValues(values: ApiKeyFormSchemaValues): ApiKeyFormValues {
  return {
    description: values.description?.trim() || undefined,
    expiresAt: values.expiresAt || undefined,
    name: values.name.trim(),
    ownerId: values.ownerId.trim(),
    ownerType: values.ownerType,
    permissions: parseApiKeyItems(values.permissionsInput),
    scopes: parseApiKeyItems(values.scopesInput),
  };
}

function ApiKeyForm({
  error,
  isSubmitting = false,
  onCancel,
  onSubmit,
  submitLabel,
}: ApiKeyFormProps) {
  const {
    formState: { errors },
    handleSubmit,
    register,
    setValue,
    watch,
  } = useForm<ApiKeyFormSchemaValues>({
    defaultValues: {
      description: "",
      expiresAt: "",
      name: "",
      ownerId: "",
      ownerType: "service_account",
      permissionsInput: "secret.read",
      scopesInput: "global",
    },
    resolver: zodResolver(apiKeyFormSchema) as Resolver<ApiKeyFormSchemaValues>,
  });
  const selectedOwnerType = watch("ownerType");

  const handleValidSubmit = async (values: ApiKeyFormSchemaValues) => {
    await onSubmit(mapSchemaValuesToApiKeyFormValues(values));
  };

  return (
    <form
      className="w-full"
      onSubmit={(event) => {
        void handleSubmit(handleValidSubmit)(event);
      }}
    >
      <Stack>
        <FormField
          description="Use a clear technical name. Do not paste token values here."
          error={errors.name?.message}
          id="api-key-name"
          label="Name"
          required
        >
          <Input
            aria-invalid={Boolean(errors.name)}
            autoComplete="off"
            disabled={isSubmitting}
            id="api-key-name"
            placeholder="openclaw-agent-prod"
            {...register("name")}
          />
        </FormField>
        <FormField
          description="Optional non-sensitive purpose or ownership context."
          error={errors.description?.message}
          id="api-key-description"
          label="Description"
        >
          <Textarea
            aria-invalid={Boolean(errors.description)}
            disabled={isSubmitting}
            id="api-key-description"
            placeholder="Used by the production MCP agent"
            {...register("description")}
          />
        </FormField>
        <FormField
          error={errors.ownerType?.message}
          id="api-key-owner-type"
          label="Owner type"
          required
        >
          <Select
            disabled={isSubmitting}
            id="api-key-owner-type"
            onValueChange={(value) =>
              setValue("ownerType", value as ApiKeyFormSchemaValues["ownerType"])
            }
            options={ownerTypeOptions}
            value={selectedOwnerType}
          />
        </FormField>
        <FormField
          description="Backend-owned actor or service account identifier."
          error={errors.ownerId?.message}
          id="api-key-owner-id"
          label="Owner ID"
          required
        >
          <Input
            aria-invalid={Boolean(errors.ownerId)}
            autoComplete="off"
            disabled={isSubmitting}
            id="api-key-owner-id"
            placeholder="service-account-id"
            {...register("ownerId")}
          />
        </FormField>
        <FormField
          description="Comma-separated permissions. The backend remains the authorization authority."
          error={errors.permissionsInput?.message}
          id="api-key-permissions"
          label="Permissions"
          required
        >
          <Input
            aria-invalid={Boolean(errors.permissionsInput)}
            autoComplete="off"
            disabled={isSubmitting}
            id="api-key-permissions"
            placeholder="secret.read, secret.version.read"
            {...register("permissionsInput")}
          />
        </FormField>
        <FormField
          description="Comma-separated scopes or contexts."
          error={errors.scopesInput?.message}
          id="api-key-scopes"
          label="Scopes"
          required
        >
          <Input
            aria-invalid={Boolean(errors.scopesInput)}
            autoComplete="off"
            disabled={isSubmitting}
            id="api-key-scopes"
            placeholder="global, vault:production"
            {...register("scopesInput")}
          />
        </FormField>
        <FormField
          description="Optional expiration date. Leave empty only when policy allows non-expiring keys."
          error={errors.expiresAt?.message}
          id="api-key-expires-at"
          label="Expiration"
        >
          <Input
            aria-invalid={Boolean(errors.expiresAt)}
            disabled={isSubmitting}
            id="api-key-expires-at"
            type="date"
            {...register("expiresAt")}
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

export { ApiKeyForm, mapSchemaValuesToApiKeyFormValues };
export type { ApiKeyFormProps };
