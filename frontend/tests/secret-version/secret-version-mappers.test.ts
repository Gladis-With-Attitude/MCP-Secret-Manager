import { describe, expect, it } from "vitest";

import {
  mapSecretVersionDtoToSecretVersion,
  mapSecretVersionFiltersToParams,
  mapSecretVersionFormToCreateDto,
  mapSecretVersionListResponseToSecretVersionList,
} from "@/features/secret-version/mappers/secret-version-mappers";

describe("secret version mappers", () => {
  it("maps version metadata without exposing backend value fields", () => {
    const version = mapSecretVersionDtoToSecretVersion({
      active: true,
      created_at: "2026-01-01T00:00:00Z",
      id: "version_1",
      secret_id: "secret_1",
      value: "must-not-be-mapped",
      version: 1,
    });

    expect(version).toMatchObject({
      id: "version_1",
      isCurrent: true,
      secretId: "secret_1",
      status: "active",
      version: 1,
    });
    expect(JSON.stringify(version)).not.toContain("must-not-be-mapped");
  });

  it("sorts version list newest first and maps permissions", () => {
    const list = mapSecretVersionListResponseToSecretVersionList(
      {
        data: [
          { id: "version_1", secret_id: "secret_1", version: 1 },
          { id: "version_3", secret_id: "secret_1", version: 3 },
        ],
        pagination: { page: 1, pageSize: 20, total: 2 },
        permissions: { create: true, restore: false },
        success: true,
      },
      "secret_1",
    );

    expect(list.items.map((version) => version.version)).toEqual([3, 1]);
    expect(list.permissions).toMatchObject({ create: true, restore: false });
  });

  it("maps filters and form values to transport DTOs", () => {
    expect(mapSecretVersionFiltersToParams({ currentOnly: true, status: "current" })).toEqual({
      current_only: true,
      page: undefined,
      page_size: undefined,
      status: "current",
    });
    expect(
      mapSecretVersionFormToCreateDto({
        makeCurrent: true,
        metadata: { source: "manual" },
        note: " rotated ",
        value: "sensitive-value",
      }),
    ).toEqual({
      make_current: true,
      metadata: { source: "manual" },
      note: "rotated",
      value: "sensitive-value",
    });
  });
});
