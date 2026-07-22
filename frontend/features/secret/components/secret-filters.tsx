"use client";

import { Button } from "@/components/buttons/button";
import { Select } from "@/components/forms/select";

import type { SecretStatus, SecretType } from "../types/secret";
import { SecretSearch } from "./secret-search";
import { typeLabel } from "./secret-type-badge";

type SecretFiltersProps = {
  onReset: () => void;
  onSearchChange: (value: string) => void;
  onStatusChange: (value: SecretStatus | "all") => void;
  onTypeChange: (value: SecretType | "all") => void;
  search: string;
  status: SecretStatus | "all";
  type: SecretType | "all";
};

function SecretFilters({
  onReset,
  onSearchChange,
  onStatusChange,
  onTypeChange,
  search,
  status,
  type,
}: SecretFiltersProps) {
  return (
    <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
      <SecretSearch onSearchChange={onSearchChange} search={search} />
      <Select
        onValueChange={(value) => onStatusChange(value as SecretStatus | "all")}
        options={[
          { label: "All statuses", value: "all" },
          { label: "Active", value: "active" },
          { label: "Archived", value: "archived" },
          { label: "Deleted", value: "deleted" },
          { label: "Missing version", value: "missing_version" },
        ]}
        value={status}
      />
      <Select
        onValueChange={(value) => onTypeChange(value as SecretType | "all")}
        options={[
          { label: "All types", value: "all" },
          { label: typeLabel.generic, value: "generic" },
          { label: typeLabel.api_key, value: "api_key" },
          { label: typeLabel.password, value: "password" },
          { label: typeLabel.token, value: "token" },
          { label: typeLabel.certificate, value: "certificate" },
          { label: typeLabel.other, value: "other" },
        ]}
        value={type}
      />
      <Button onClick={onReset} variant="outline">
        Reset
      </Button>
    </div>
  );
}

export { SecretFilters };
export type { SecretFiltersProps };
