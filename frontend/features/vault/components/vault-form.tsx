"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { Button } from "@/components/buttons/button";
import { FormField } from "@/components/forms/form-field";
import { Input } from "@/components/forms/input";
import { Textarea } from "@/components/forms/textarea";
import { Stack } from "@/components/layout/stack";

import type { Vault, VaultFormValues } from "../types/vault";
import { vaultFormSchema, type VaultFormSchemaValues } from "../validation/vault-schema";

type VaultFormProps = {
  error?: string | null;
  isSubmitting?: boolean;
  onCancel?: () => void;
  onSubmit: (values: VaultFormValues) => void | Promise<void>;
  submitLabel: string;
  vault?: Vault;
};

function VaultForm({
  error,
  isSubmitting = false,
  onCancel,
  onSubmit,
  submitLabel,
  vault,
}: VaultFormProps) {
  const {
    formState: { errors },
    handleSubmit,
    register,
  } = useForm<VaultFormSchemaValues>({
    defaultValues: {
      description: vault?.description ?? "",
      name: vault?.name ?? "",
    },
    resolver: zodResolver(vaultFormSchema),
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
          description="Use a clear name that identifies this security boundary."
          error={errors.name?.message}
          id="vault-name"
          label="Name"
          required
        >
          <Input
            aria-invalid={Boolean(errors.name)}
            autoComplete="off"
            disabled={isSubmitting}
            id="vault-name"
            placeholder="Production"
            {...register("name")}
          />
        </FormField>
        <FormField
          description="Optional non-sensitive context for operators."
          error={errors.description?.message}
          id="vault-description"
          label="Description"
        >
          <Textarea
            aria-invalid={Boolean(errors.description)}
            disabled={isSubmitting}
            id="vault-description"
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

export { VaultForm };
export type { VaultFormProps };
