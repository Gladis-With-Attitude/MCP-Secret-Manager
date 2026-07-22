"use client";

import { useMemo, useState } from "react";

import type { SecretListFilters, SecretStatus, SecretType } from "../types/secret";

function useSecretFilters(initialFilters: SecretListFilters = {}) {
  const [page, setPage] = useState(initialFilters.page ?? 1);
  const [pageSize] = useState(initialFilters.pageSize ?? 20);
  const [search, setSearch] = useState(initialFilters.search ?? "");
  const [status, setStatus] = useState<SecretStatus | "all">(initialFilters.status ?? "all");
  const [type, setType] = useState<SecretType | "all">(initialFilters.type ?? "all");

  const filters = useMemo<SecretListFilters>(
    () => ({
      page,
      pageSize,
      search,
      status,
      type,
    }),
    [page, pageSize, search, status, type],
  );

  const resetFilters = () => {
    setPage(1);
    setSearch("");
    setStatus("all");
    setType("all");
  };

  const updateSearch = (value: string) => {
    setPage(1);
    setSearch(value);
  };

  const updateStatus = (value: SecretStatus | "all") => {
    setPage(1);
    setStatus(value);
  };

  const updateType = (value: SecretType | "all") => {
    setPage(1);
    setType(value);
  };

  return {
    filters,
    page,
    pageSize,
    resetFilters,
    search,
    setPage,
    setSearch: updateSearch,
    setStatus: updateStatus,
    setType: updateType,
    status,
    type,
  };
}

export { useSecretFilters };
