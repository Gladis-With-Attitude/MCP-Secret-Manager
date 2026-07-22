"use client";

import { Search } from "lucide-react";

import { Input } from "@/components/forms/input";

type SecretSearchProps = {
  onSearchChange: (value: string) => void;
  search: string;
};

function SecretSearch({ onSearchChange, search }: SecretSearchProps) {
  return (
    <div className="relative w-full sm:max-w-sm">
      <Search
        aria-hidden="true"
        className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
      />
      <Input
        aria-label="Search secrets"
        className="pl-9"
        onChange={(event) => onSearchChange(event.target.value)}
        placeholder="Search metadata"
        value={search}
      />
    </div>
  );
}

export { SecretSearch };
export type { SecretSearchProps };
