"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import type { Resolver } from "react-hook-form";
import { useForm } from "react-hook-form";

import { Button } from "@/components/buttons/button";
import { FormField } from "@/components/forms/form-field";
import { Input } from "@/components/forms/input";
import { Stack } from "@/components/layout/stack";

import type { ProfileFormValues, UserProfile } from "../types/profile";
import { profileFormSchema, type ProfileFormSchemaValues } from "../validation/profile-schema";
import { AvatarUploader } from "./avatar-uploader";

type ProfileFormProps = {
  error?: string | null;
  isSubmitting?: boolean;
  onSubmit: (values: ProfileFormValues) => void | Promise<void>;
  profile: UserProfile;
  readOnly?: boolean;
};

function mapSchemaValuesToProfileFormValues(values: ProfileFormSchemaValues): ProfileFormValues {
  return {
    email: values.email?.trim() || undefined,
    name: values.name.trim(),
    organization: values.organization?.trim() || undefined,
  };
}

function ProfileForm({
  error,
  isSubmitting = false,
  onSubmit,
  profile,
  readOnly = false,
}: ProfileFormProps) {
  const {
    formState: { errors },
    handleSubmit,
    register,
  } = useForm<ProfileFormSchemaValues>({
    defaultValues: {
      email: profile.email ?? "",
      name: profile.name,
      organization: profile.organization ?? "",
    },
    resolver: zodResolver(profileFormSchema) as Resolver<ProfileFormSchemaValues>,
  });

  async function handleValidSubmit(values: ProfileFormSchemaValues) {
    await onSubmit(mapSchemaValuesToProfileFormValues(values));
  }

  return (
    <form
      className="w-full"
      onSubmit={(event) => {
        void handleSubmit(handleValidSubmit)(event);
      }}
    >
      <Stack>
        <AvatarUploader value={profile.avatarUrl} />
        <FormField error={errors.name?.message} id="profile-name" label="Name" required>
          <Input
            aria-invalid={Boolean(errors.name)}
            autoComplete="name"
            disabled={isSubmitting || readOnly}
            id="profile-name"
            {...register("name")}
          />
        </FormField>
        <FormField
          description={
            profile.emailEditable
              ? "Managed by the backend."
              : "Read-only when managed by the identity provider."
          }
          error={errors.email?.message}
          id="profile-email"
          label="Email"
        >
          <Input
            aria-invalid={Boolean(errors.email)}
            autoComplete="email"
            disabled={isSubmitting || readOnly || !profile.emailEditable}
            id="profile-email"
            readOnly={!profile.emailEditable}
            type="email"
            {...register("email")}
          />
        </FormField>
        <FormField
          error={errors.organization?.message}
          id="profile-organization"
          label="Organization"
        >
          <Input
            aria-invalid={Boolean(errors.organization)}
            autoComplete="organization"
            disabled={isSubmitting || readOnly}
            id="profile-organization"
            {...register("organization")}
          />
        </FormField>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        <div className="flex justify-end">
          <Button disabled={readOnly} isLoading={isSubmitting} type="submit">
            Save profile
          </Button>
        </div>
      </Stack>
    </form>
  );
}

export { mapSchemaValuesToProfileFormValues, ProfileForm };
export type { ProfileFormProps };
