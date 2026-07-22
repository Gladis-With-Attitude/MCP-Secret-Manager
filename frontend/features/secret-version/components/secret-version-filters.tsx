"use client";

import { Button } from "@/components/buttons/button";
import { Checkbox } from "@/components/forms/checkbox";
import { FormField } from "@/components/forms/form-field";
import { Select } from "@/components/forms/select";
import { Grid } from "@/components/layout/grid";

import type { SecretVersionStatus } from "../types/secret-version";

type SecretVersionFiltersProps = {
  currentOnly: boolean;
  onCurrentOnlyChange: (checked: boolean) => void;
  onReset: () => void;
  onStatusChange: (status: SecretVersionStatus | "all") => void;
  status: SecretVersionStatus | "all";
};

const statusOptions = [
  { label: "All statuses", value: "all" },
  { label: "Current", value: "current" },
  { label: "Active", value: "active" },
  { label: "Deprecated", value: "deprecated" },
  { label: "Revoked", value: "revoked" },
  { label: "Destroyed", value: "destroyed" },
];

function SecretVersionFilters({
  currentOnly,
  onCurrentOnlyChange,
  onReset,
  onStatusChange,
  status,
}: SecretVersionFiltersProps) {
  return (
    <div className="grid gap-4 md:grid-cols-[1fr_auto] md:items-end">
      <Grid columns={2}>
        <FormField id="version-status" label="Status">
          <Select
            id="version-status"
            onValueChange={(value) => onStatusChange(value as SecretVersionStatus | "all")}
            options={statusOptions}
            value={status}
          />
        </FormField>
        <div className="flex items-center pt-6">
          <Checkbox
            checked={currentOnly}
            label="Current only"
            onCheckedChange={(checked) => onCurrentOnlyChange(checked === true)}
          />
        </div>
      </Grid>
      <Button onClick={onReset} variant="outline">
        Reset filters
      </Button>
    </div>
  );
}

export { SecretVersionFilters };
export type { SecretVersionFiltersProps };
