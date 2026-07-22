"use client";

import { useMemo, useState } from "react";

import type { ApiKeyListFilters, ApiKeyStatus } from "../types/api-key";

function useApiKeyFilters() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<ApiKeyStatus | "all">("all");

  const filters = useMemo<ApiKeyListFilters>(
    () => ({
      page,
      search,
      status,
    }),
    [page, search, status],
  );

  function resetFilters() {
    setPage(1);
    setSearch("");
    setStatus("all");
  }

  return {
    filters,
    page,
    resetFilters,
    search,
    setPage,
    setSearch,
    setStatus,
    status,
  };
}

export { useApiKeyFilters };
