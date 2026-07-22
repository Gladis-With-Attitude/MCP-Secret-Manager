import { act, renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { useApiKeyFilters } from "@/features/api-key";

describe("useApiKeyFilters", () => {
  it("tracks API key list filters", () => {
    const { result } = renderHook(() => useApiKeyFilters());

    act(() => {
      result.current.setSearch("agent");
      result.current.setStatus("active");
      result.current.setPage(2);
    });

    expect(result.current.filters).toEqual({
      page: 2,
      search: "agent",
      status: "active",
    });

    act(() => result.current.resetFilters());

    expect(result.current.filters).toEqual({
      page: 1,
      search: "",
      status: "all",
    });
  });
});
