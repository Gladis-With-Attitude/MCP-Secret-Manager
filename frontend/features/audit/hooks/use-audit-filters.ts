"use client";

import { useMemo } from "react";

import { usePathname, useRouter, useSearchParams } from "next/navigation";

import type { AuditFilterFormValues, AuditFilterResult, AuditFilters } from "../types/audit";
import { AUDIT_DEFAULT_LIMIT } from "../validation/audit-schema";

function getParam(searchParams: URLSearchParams, key: string): string | undefined {
  return searchParams.get(key) || undefined;
}

function parseResult(value: string | undefined): AuditFilterResult {
  if (value === "success" || value === "failure") {
    return value;
  }

  return "all";
}

function parseNumber(value: string | undefined, fallback: number): number {
  const parsed = value ? Number(value) : Number.NaN;

  return Number.isFinite(parsed) && parsed >= 0 ? parsed : fallback;
}

function filtersToSearchParams(filters: AuditFilters): URLSearchParams {
  const next = new URLSearchParams();

  if (filters.query) next.set("q", filters.query);
  if (filters.actorId) next.set("actorId", filters.actorId);
  if (filters.action) next.set("action", filters.action);
  if (filters.resourceType) next.set("resourceType", filters.resourceType);
  if (filters.resourceId) next.set("resourceId", filters.resourceId);
  if (filters.result && filters.result !== "all") next.set("result", filters.result);
  if (filters.startDate) next.set("startDate", filters.startDate);
  if (filters.endDate) next.set("endDate", filters.endDate);
  if (filters.limit && filters.limit !== AUDIT_DEFAULT_LIMIT)
    next.set("limit", String(filters.limit));
  if (filters.offset) next.set("offset", String(filters.offset));

  return next;
}

function useAuditFilters() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const filters = useMemo<AuditFilters>(
    () => ({
      action: getParam(searchParams, "action"),
      actorId: getParam(searchParams, "actorId"),
      endDate: getParam(searchParams, "endDate"),
      limit: parseNumber(getParam(searchParams, "limit"), AUDIT_DEFAULT_LIMIT),
      offset: parseNumber(getParam(searchParams, "offset"), 0),
      query: getParam(searchParams, "q"),
      resourceId: getParam(searchParams, "resourceId"),
      resourceType: getParam(searchParams, "resourceType"),
      result: parseResult(getParam(searchParams, "result")),
      startDate: getParam(searchParams, "startDate"),
    }),
    [searchParams],
  );

  const formValues = useMemo<AuditFilterFormValues>(
    () => ({
      action: filters.action ?? "",
      actorId: filters.actorId ?? "",
      endDate: filters.endDate ?? "",
      query: filters.query ?? "",
      resourceId: filters.resourceId ?? "",
      resourceType: filters.resourceType ?? "",
      result: filters.result ?? "all",
      startDate: filters.startDate ?? "",
    }),
    [filters],
  );

  function applyFilters(nextFilters: AuditFilters) {
    const params = filtersToSearchParams(nextFilters);
    const query = params.toString();

    router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  function resetFilters() {
    router.replace(pathname, { scroll: false });
  }

  function setOffset(offset: number) {
    applyFilters({ ...filters, offset: Math.max(0, offset) });
  }

  return {
    applyFilters,
    filters,
    formValues,
    resetFilters,
    setOffset,
  };
}

export { filtersToSearchParams, useAuditFilters };
