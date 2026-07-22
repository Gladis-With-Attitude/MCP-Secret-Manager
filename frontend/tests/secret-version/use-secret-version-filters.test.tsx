import { act, renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { useSecretVersionFilters } from "@/features/secret-version";

describe("useSecretVersionFilters", () => {
  it("tracks metadata filters and resets them", () => {
    const { result } = renderHook(() => useSecretVersionFilters());

    act(() => {
      result.current.setStatus("current");
      result.current.setCurrentOnly(true);
      result.current.setPage(2);
    });

    expect(result.current.filters).toEqual({
      currentOnly: true,
      page: 2,
      status: "current",
    });

    act(() => result.current.resetFilters());

    expect(result.current.filters).toEqual({
      currentOnly: false,
      page: 1,
      status: "all",
    });
  });
});
