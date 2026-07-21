import { act } from "react";

import { renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { useVaultFilters } from "@/features/vault/hooks/use-vault-filters";

describe("useVaultFilters", () => {
  it("builds list filters and resets pagination when filters change", () => {
    const { result } = renderHook(() => useVaultFilters({ page: 3, search: "prod" }));

    expect(result.current.filters).toEqual({
      page: 3,
      pageSize: 20,
      search: "prod",
      status: "all",
    });

    act(() => result.current.setSearch("staging"));

    expect(result.current.filters.page).toBe(1);
    expect(result.current.filters.search).toBe("staging");

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
