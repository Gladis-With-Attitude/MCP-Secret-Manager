import { describe, expect, it } from "vitest";

import { serializeQueryParams } from "@/lib/api/params";

describe("serializeQueryParams", () => {
  it("serializes scalar and array parameters", () => {
    expect(
      serializeQueryParams({
        active: true,
        limit: 20,
        search: "alpha",
        status: ["ready", "paused"],
      }),
    ).toBe("?active=true&limit=20&search=alpha&status=ready&status=paused");
  });

  it("omits empty, null and undefined values", () => {
    expect(
      serializeQueryParams({
        empty: "",
        missing: undefined,
        none: null,
        page: 1,
      }),
    ).toBe("?page=1");
  });
});
