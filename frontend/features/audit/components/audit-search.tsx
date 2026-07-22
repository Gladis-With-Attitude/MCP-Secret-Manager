"use client";

import { FormField } from "@/components/forms/form-field";
import { Input } from "@/components/forms/input";

type AuditSearchProps = {
  disabled?: boolean;
  error?: string;
  onChange: (value: string) => void;
  value: string;
};

function AuditSearch({ disabled = false, error, onChange, value }: AuditSearchProps) {
  return (
    <FormField
      description="Search safe audit metadata, event id, actor, resource or action."
      error={error}
      id="audit-search"
      label="Search"
    >
      <Input
        aria-invalid={Boolean(error)}
        disabled={disabled}
        id="audit-search"
        onChange={(event) => onChange(event.target.value)}
        placeholder="Search audit logs"
        value={value}
      />
    </FormField>
  );
}

export { AuditSearch };
export type { AuditSearchProps };
