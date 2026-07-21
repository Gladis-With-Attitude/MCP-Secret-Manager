"use client";

import { useMemo, useState } from "react";

import type { ProjectListFilters, ProjectStatus } from "../types/project";

function useProjectFilters(initialFilters: ProjectListFilters = {}) {
  const [page, setPage] = useState(initialFilters.page ?? 1);
  const [pageSize] = useState(initialFilters.pageSize ?? 20);
  const [search, setSearch] = useState(initialFilters.search ?? "");
  const [status, setStatus] = useState<ProjectStatus | "all">(initialFilters.status ?? "all");

  const filters = useMemo<ProjectListFilters>(
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

  const updateStatus = (value: ProjectStatus | "all") => {
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

export { useProjectFilters };
