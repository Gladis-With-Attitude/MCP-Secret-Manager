"use client";

import { Search } from "lucide-react";

import { Button } from "@/components/buttons/button";
import { Input } from "@/components/forms/input";
import { Select } from "@/components/forms/select";

import type { ProjectStatus } from "../types/project";

type ProjectFiltersProps = {
  onReset: () => void;
  onSearchChange: (value: string) => void;
  onStatusChange: (value: ProjectStatus | "all") => void;
  search: string;
  status: ProjectStatus | "all";
};

function ProjectFilters({
  onReset,
  onSearchChange,
  onStatusChange,
  search,
  status,
}: ProjectFiltersProps) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
      <div className="relative w-full sm:max-w-sm">
        <Search
          aria-hidden="true"
          className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
        />
        <Input
          aria-label="Search projects"
          className="pl-9"
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder="Search projects"
          value={search}
        />
      </div>
      <Select
        onValueChange={(value) => onStatusChange(value as ProjectStatus | "all")}
        options={[
          { label: "All statuses", value: "all" },
          { label: "Active", value: "active" },
          { label: "Archived", value: "archived" },
        ]}
        value={status}
      />
      <Button onClick={onReset} variant="outline">
        Reset
      </Button>
    </div>
  );
}

export { ProjectFilters };
export type { ProjectFiltersProps };
