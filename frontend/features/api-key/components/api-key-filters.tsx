"use client";

import { Button } from "@/components/buttons/button";
import { FormField } from "@/components/forms/form-field";
import { Input } from "@/components/forms/input";
import { Select } from "@/components/forms/select";
import { Grid } from "@/components/layout/grid";

import type { ApiKeyStatus } from "../types/api-key";

type ApiKeyFiltersProps = {
  onReset: () => void;
  onSearchChange: (search: string) => void;
  onStatusChange: (status: ApiKeyStatus | "all") => void;
  search: string;
  status: ApiKeyStatus | "all";
};

const statusOptions = [
  { label: "All statuses", value: "all" },
  { label: "Active", value: "active" },
  { label: "Expired", value: "expired" },
  { label: "Revoked", value: "revoked" },
];

function ApiKeyFilters({
  onReset,
  onSearchChange,
  onStatusChange,
  search,
  status,
}: ApiKeyFiltersProps) {
  return (
    <div className="grid gap-4 md:grid-cols-[1fr_auto] md:items-end">
      <Grid columns={2}>
        <FormField id="api-key-search" label="Search">
          <Input
            id="api-key-search"
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder="Search API keys"
            value={search}
          />
        </FormField>
        <FormField id="api-key-status" label="Status">
          <Select
            id="api-key-status"
            onValueChange={(value) => onStatusChange(value as ApiKeyStatus | "all")}
            options={statusOptions}
            value={status}
          />
        </FormField>
      </Grid>
      <Button onClick={onReset} variant="outline">
        Reset filters
      </Button>
    </div>
  );
}

export { ApiKeyFilters };
export type { ApiKeyFiltersProps };
