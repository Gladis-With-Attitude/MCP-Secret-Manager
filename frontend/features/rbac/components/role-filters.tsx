"use client";

import { Button } from "@/components/buttons/button";
import { FormField } from "@/components/forms/form-field";
import { Input } from "@/components/forms/input";
import { Select } from "@/components/forms/select";

import type { RoleKind, RoleStatus } from "../types/rbac";

type RoleFiltersProps = {
  kind: "all" | RoleKind;
  onKindChange: (value: "all" | RoleKind) => void;
  onReset: () => void;
  onSearchChange: (value: string) => void;
  onStatusChange: (value: "all" | RoleStatus) => void;
  search: string;
  status: "all" | RoleStatus;
};

const kindOptions = [
  { label: "All kinds", value: "all" },
  { label: "Custom", value: "custom" },
  { label: "System", value: "system" },
];

const statusOptions = [
  { label: "All statuses", value: "all" },
  { label: "Active", value: "active" },
  { label: "Inactive", value: "inactive" },
];

function RoleFilters({
  kind,
  onKindChange,
  onReset,
  onSearchChange,
  onStatusChange,
  search,
  status,
}: RoleFiltersProps) {
  return (
    <div className="grid gap-4 md:grid-cols-[minmax(0,1fr)_180px_180px_auto] md:items-end">
      <FormField id="rbac-search" label="Search">
        <Input
          id="rbac-search"
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder="Role name or permission"
          type="search"
          value={search}
        />
      </FormField>
      <FormField id="rbac-kind" label="Kind">
        <Select
          id="rbac-kind"
          onValueChange={(value) => onKindChange(value as "all" | RoleKind)}
          options={kindOptions}
          value={kind}
        />
      </FormField>
      <FormField id="rbac-status" label="Status">
        <Select
          id="rbac-status"
          onValueChange={(value) => onStatusChange(value as "all" | RoleStatus)}
          options={statusOptions}
          value={status}
        />
      </FormField>
      <Button onClick={onReset} type="button" variant="outline">
        Reset
      </Button>
    </div>
  );
}

export { RoleFilters };
export type { RoleFiltersProps };
