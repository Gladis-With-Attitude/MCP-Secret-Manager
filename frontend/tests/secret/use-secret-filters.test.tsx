import { act } from "react";

import { renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { useSecretFilters } from "@/features/secret/hooks/use-secret-filters";

describe("useSecretFilters", () => {
  it("builds filters and resets pagination when search or filters change", () => {
    const { result } = renderHook(() => useSecretFilters({ page: 3, search: "api" }));

    expect(result.current.filters).toEqual({
      page: 3,
      pageSize: 20,
      search: "api",
      status: "all",
      type: "all",
    });

    act(() => result.current.setSearch("database"));
    expect(result.current.filters.page).toBe(1);
    expect(result.current.filters.search).toBe("database");

    act(() => result.current.setType("password"));
    expect(result.current.filters.type).toBe("password");

    act(() => result.current.resetFilters());
    expect(result.current.filters).toEqual({
      page: 1,
      pageSize: 20,
      search: "",
      status: "all",
      type: "all",
    });
  });
});
