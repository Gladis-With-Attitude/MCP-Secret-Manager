"use client";

import { useMemo, useState } from "react";

import type { RoleFilters, RoleKind, RoleStatus } from "../types/rbac";
import { RBAC_DEFAULT_LIMIT } from "../validation/rbac-schema";

function useRbacFilters() {
  const [kind, setKind] = useState<"all" | RoleKind>("all");
  const [page, setPage] = useState(1);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<"all" | RoleStatus>("all");

  const filters = useMemo<RoleFilters>(
    () => ({
      kind,
      limit: RBAC_DEFAULT_LIMIT,
      offset: (page - 1) * RBAC_DEFAULT_LIMIT,
      query,
      status,
    }),
    [kind, page, query, status],
  );

  function resetFilters() {
    setKind("all");
    setPage(1);
    setQuery("");
    setStatus("all");
  }

  return {
    filters,
    kind,
    page,
    query,
    resetFilters,
    setKind: (value: "all" | RoleKind) => {
      setKind(value);
      setPage(1);
    },
    setPage,
    setQuery: (value: string) => {
      setQuery(value);
      setPage(1);
    },
    setStatus: (value: "all" | RoleStatus) => {
      setStatus(value);
      setPage(1);
    },
    status,
  };
}

export { useRbacFilters };
