"use client";

import { FormField } from "@/components/forms/form-field";
import { Input } from "@/components/forms/input";

type AvatarUploaderProps = {
  disabled?: boolean;
  value?: string;
};

function AvatarUploader({ disabled = true, value }: AvatarUploaderProps) {
  return (
    <FormField
      description="Avatar upload is available only when the backend exposes it. Do not paste tokens or signed URLs."
      id="profile-avatar"
      label="Avatar URL"
    >
      <Input
        disabled={disabled}
        id="profile-avatar"
        placeholder="Managed by identity provider"
        readOnly
        value={value ?? ""}
      />
    </FormField>
  );
}

export { AvatarUploader };
export type { AvatarUploaderProps };
