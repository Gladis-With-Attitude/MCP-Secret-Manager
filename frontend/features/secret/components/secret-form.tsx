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

import {
  mapSecretSchemaValuesToFormValues,
  mapSecretToFormDefaults,
} from "../mappers/secret-mappers";
import type { Secret, SecretFormValues } from "../types/secret";
import {
  secretCreateFormSchema,
  type SecretCreateFormSchemaValues,
  secretMetadataFormSchema,
  secretTypeOptions,
} from "../validation/secret-schema";
import { typeLabel } from "./secret-type-badge";

type SecretFormProps = {
  error?: string | null;
  includeValue?: boolean;
  isSubmitting?: boolean;
  onCancel?: () => void;
  onSubmit: (values: SecretFormValues) => void | Promise<void>;
  projectName?: string | null;
  secret?: Secret;
  submitLabel: string;
};

const typeOptions = secretTypeOptions.map((option) => ({
  label: typeLabel[option],
  value: option,
}));

function SecretForm({
  error,
  includeValue = false,
  isSubmitting = false,
  onCancel,
  onSubmit,
  projectName,
  secret,
  submitLabel,
}: SecretFormProps) {
  const resolver = zodResolver(
    includeValue ? secretCreateFormSchema : secretMetadataFormSchema,
  ) as unknown as Resolver<SecretCreateFormSchemaValues>;
  const {
    formState: { errors },
    handleSubmit,
    register,
    resetField,
    setValue,
    watch,
  } = useForm<SecretCreateFormSchemaValues>({
    defaultValues: mapSecretToFormDefaults(secret),
    resolver,
  });
  const selectedType = watch("type");

  const handleValidSubmit = async (values: SecretCreateFormSchemaValues) => {
    await onSubmit(mapSecretSchemaValuesToFormValues(values));

    if (includeValue) {
      resetField("value", { defaultValue: "" });
    }
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
          description={
            projectName
              ? `This secret belongs to ${projectName}. Values are never stored in browser storage.`
              : "This secret belongs to the current project context."
          }
          error={errors.name?.message}
          id="secret-name"
          label="Name"
          required
        >
          <Input
            aria-invalid={Boolean(errors.name)}
            autoComplete="off"
            disabled={isSubmitting || Boolean(secret)}
            id="secret-name"
            placeholder="DATABASE_PASSWORD"
            {...register("name")}
          />
        </FormField>
        <FormField error={errors.type?.message} id="secret-type" label="Type" required>
          <Select
            disabled={isSubmitting}
            id="secret-type"
            onValueChange={(value) =>
              setValue("type", value as SecretCreateFormSchemaValues["type"])
            }
            options={typeOptions}
            value={selectedType}
          />
        </FormField>
        <FormField
          description="Optional non-sensitive context. Never put secret values here."
          error={errors.description?.message}
          id="secret-description"
          label="Description"
        >
          <Textarea
            aria-invalid={Boolean(errors.description)}
            disabled={isSubmitting}
            id="secret-description"
            placeholder="Short non-sensitive description"
            {...register("description")}
          />
        </FormField>
        <FormField
          description="Comma-separated non-sensitive tags."
          error={errors.tagsInput?.message}
          id="secret-tags"
          label="Tags"
        >
          <Input
            aria-invalid={Boolean(errors.tagsInput)}
            disabled={isSubmitting}
            id="secret-tags"
            placeholder="production, database"
            {...register("tagsInput")}
          />
        </FormField>
        <FormField
          description="Optional JSON object with non-sensitive metadata only."
          error={errors.metadataJson?.message}
          id="secret-metadata"
          label="Metadata"
        >
          <Textarea
            aria-invalid={Boolean(errors.metadataJson)}
            disabled={isSubmitting}
            id="secret-metadata"
            placeholder='{"owner":"platform"}'
            {...register("metadataJson")}
          />
        </FormField>
        {includeValue ? (
          <FormField
            description="The frontend sends this value to the backend without encrypting it and clears the field after submit."
            error={errors.value?.message}
            id="secret-value"
            label="Initial value"
            required
          >
            <Textarea
              aria-invalid={Boolean(errors.value)}
              autoComplete="off"
              disabled={isSubmitting}
              id="secret-value"
              placeholder="Paste secret value"
              {...register("value")}
            />
          </FormField>
        ) : null}
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

export { SecretForm };
export type { SecretFormProps };
