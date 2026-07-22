import { renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { filtersToSearchParams, useAuditFilters } from "@/features/audit";

const replace = vi.fn();
let params = new URLSearchParams();

vi.mock("next/navigation", () => ({
  usePathname: () => "/audit",
  useRouter: () => ({ replace }),
  useSearchParams: () => params,
}));

describe("useAuditFilters", () => {
  beforeEach(() => {
    replace.mockClear();
    params = new URLSearchParams("q=secret&result=failure&offset=100");
  });

  it("reads filters from URL search params", () => {
    const { result } = renderHook(() => useAuditFilters());

    expect(result.current.filters).toMatchObject({
      offset: 100,
      query: "secret",
      result: "failure",
    });
  });

  it("preserves filters in URL when applying pagination", () => {
    const { result } = renderHook(() => useAuditFilters());

    result.current.setOffset(200);

    expect(replace).toHaveBeenCalledWith("/audit?q=secret&result=failure&offset=200", {
      scroll: false,
    });
  });

  it("serializes filters predictably", () => {
    expect(
      filtersToSearchParams({
        action: "secret.read",
        limit: 50,
        query: "secret",
        result: "success",
      }).toString(),
    ).toBe("q=secret&action=secret.read&result=success&limit=50");
  });
});
