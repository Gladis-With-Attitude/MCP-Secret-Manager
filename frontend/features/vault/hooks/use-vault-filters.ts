"use client";

import { useMemo, useState } from "react";

import type { VaultListFilters, VaultStatus } from "../types/vault";

function useVaultFilters(initialFilters: VaultListFilters = {}) {
  const [page, setPage] = useState(initialFilters.page ?? 1);
  const [pageSize] = useState(initialFilters.pageSize ?? 20);
  const [search, setSearch] = useState(initialFilters.search ?? "");
  const [status, setStatus] = useState<VaultStatus | "all">(initialFilters.status ?? "all");

  const filters = useMemo<VaultListFilters>(
    () => ({
      page,
      pageSize,
      search,
      status,
    }),
    [page, pageSize, search, status],
  );

  const resetFilters = () => {
    setPage(1);
    setSearch("");
    setStatus("all");
  };

  const updateSearch = (value: string) => {
    setPage(1);
    setSearch(value);
  };

  const updateStatus = (value: VaultStatus | "all") => {
    setPage(1);
    setStatus(value);
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
    status,
  };
}

export { useVaultFilters };
