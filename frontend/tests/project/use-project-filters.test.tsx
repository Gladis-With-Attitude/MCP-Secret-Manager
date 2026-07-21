import { act } from "react";

import { renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { useProjectFilters } from "@/features/project/hooks/use-project-filters";

describe("useProjectFilters", () => {
  it("builds list filters and resets pagination when filters change", () => {
    const { result } = renderHook(() => useProjectFilters({ page: 3, search: "api" }));

    expect(result.current.filters).toEqual({
      page: 3,
      pageSize: 20,
      search: "api",
      status: "all",
    });

    act(() => result.current.setSearch("worker"));

    expect(result.current.filters.page).toBe(1);
    expect(result.current.filters.search).toBe("worker");

    act(() => result.current.setStatus("archived"));

    expect(result.current.filters.status).toBe("archived");

    act(() => result.current.resetFilters());

    expect(result.current.filters).toEqual({
      page: 1,
      pageSize: 20,
      search: "",
      status: "all",
    });
  });
});
