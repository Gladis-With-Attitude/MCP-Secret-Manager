"use client";

import { useMemo, useState } from "react";

import type { SecretVersionListFilters, SecretVersionStatus } from "../types/secret-version";

function useSecretVersionFilters() {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState<SecretVersionStatus | "all">("all");
  const [currentOnly, setCurrentOnly] = useState(false);

  const filters = useMemo<SecretVersionListFilters>(
    () => ({
      currentOnly,
      page,
      status,
    }),
    [currentOnly, page, status],
  );

  function resetFilters() {
    setPage(1);
    setStatus("all");
    setCurrentOnly(false);
  }

  return {
    currentOnly,
    filters,
    page,
    resetFilters,
    setCurrentOnly,
    setPage,
    setStatus,
    status,
  };
}

export { useSecretVersionFilters };
