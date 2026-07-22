"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import type { Resolver } from "react-hook-form";
import { useForm } from "react-hook-form";

import { Button } from "@/components/buttons/button";
import { Checkbox } from "@/components/forms/checkbox";
import { FormField } from "@/components/forms/form-field";
import { Textarea } from "@/components/forms/textarea";
import { Stack } from "@/components/layout/stack";

import type { SecretVersionFormValues } from "../types/secret-version";
import {
  parseSecretVersionMetadata,
  secretVersionRotateFormSchema,
  type SecretVersionRotateSchemaValues,
} from "../validation/secret-version-schema";

type SecretVersionFormProps = {
  error?: string | null;
  isSubmitting?: boolean;
  onCancel?: () => void;
  onSubmit: (values: SecretVersionFormValues) => void | Promise<void>;
  secretName?: string | null;
  submitLabel: string;
};

function mapSchemaValuesToFormValues(
  values: SecretVersionRotateSchemaValues,
): SecretVersionFormValues {
  return {
    makeCurrent: values.makeCurrent,
    metadata: parseSecretVersionMetadata(values.metadataJson),
    note: values.note?.trim() || undefined,
    value: values.value,
  };
}

function SecretVersionForm({
  error,
  isSubmitting = false,
  onCancel,
  onSubmit,
  secretName,
  submitLabel,
}: SecretVersionFormProps) {
  const {
    formState: { errors },
    handleSubmit,
    register,
    resetField,
    setValue,
    watch,
  } = useForm<SecretVersionRotateSchemaValues>({
    defaultValues: {
      makeCurrent: true,
      metadataJson: "",
      note: "",
      value: "",
    },
    resolver: zodResolver(
      secretVersionRotateFormSchema,
    ) as Resolver<SecretVersionRotateSchemaValues>,
  });
  const makeCurrent = watch("makeCurrent");

  const handleValidSubmit = async (values: SecretVersionRotateSchemaValues) => {
    await onSubmit(mapSchemaValuesToFormValues(values));
    resetField("value", { defaultValue: "" });
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
            secretName
              ? `Create a new value version for ${secretName}. The browser does not persist this value.`
              : "Create a new immutable version. The backend owns encryption and key handling."
          }
          error={errors.value?.message}
          id="secret-version-value"
          label="New value"
          required
        >
          <Textarea
            aria-invalid={Boolean(errors.value)}
            autoComplete="off"
            disabled={isSubmitting}
            id="secret-version-value"
            placeholder="Paste new secret value"
            {...register("value")}
          />
        </FormField>
        <FormField
          description="Optional non-sensitive note for audit context."
          error={errors.note?.message}
          id="secret-version-note"
          label="Rotation note"
        >
          <Textarea
            aria-invalid={Boolean(errors.note)}
            disabled={isSubmitting}
            id="secret-version-note"
            placeholder="Rotated after scheduled credential renewal"
            {...register("note")}
          />
        </FormField>
        <FormField
          description="Optional JSON object with non-sensitive metadata only."
          error={errors.metadataJson?.message}
          id="secret-version-metadata"
          label="Metadata"
        >
          <Textarea
            aria-invalid={Boolean(errors.metadataJson)}
            disabled={isSubmitting}
            id="secret-version-metadata"
            placeholder='{"source":"manual-rotation"}'
            {...register("metadataJson")}
          />
        </FormField>
        <Checkbox
          checked={makeCurrent}
          disabled={isSubmitting}
          label="Mark as current version after creation"
          onCheckedChange={(checked) => setValue("makeCurrent", checked === true)}
        />
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

export { mapSchemaValuesToFormValues, SecretVersionForm };
export type { SecretVersionFormProps };
