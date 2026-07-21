import { describe, expect, it } from "vitest";

import {
  canUseVaultAction,
  mapVaultDtoToVault,
  mapVaultFiltersToParams,
  mapVaultFormToCreateDto,
  mapVaultListResponseToVaultList,
} from "@/features/vault/mappers/vault-mappers";

describe("vault mappers", () => {
  it("maps backend vault metadata to UI model", () => {
    expect(
      mapVaultDtoToVault({
        created_at: "2026-07-21T08:00:00Z",
        description: "Production metadata",
        id: "vault_1",
        locked: true,
        name: "Production",
        permissions: { archive: false, update: true },
        project_count: 2,
        secret_count: 8,
      }),
    ).toEqual({
      archived: false,
      createdAt: "2026-07-21T08:00:00Z",
      createdBy: undefined,
      description: "Production metadata",
      id: "vault_1",
      locked: true,
      name: "Production",
      permissions: {
        archive: false,
        create: undefined,
        delete: undefined,
        lock: undefined,
        read: undefined,
        update: true,
      },
      projectCount: 2,
      secretCount: 8,
      status: "locked",
      updatedAt: undefined,
    });
  });

  it("maps paginated list envelopes and top-level permissions", () => {
    const result = mapVaultListResponseToVaultList({
      data: [{ id: "vault_1", name: "Production" }],
      pagination: { page: 1, pageSize: 20, total: 1 },
      permissions: { create: true },
      success: true,
    });

    expect(result.items).toHaveLength(1);
    expect(result.pagination.total).toBe(1);
    expect(result.permissions.create).toBe(true);
  });

  it("serializes filters and trims form values", () => {
    expect(mapVaultFiltersToParams({ page: 2, search: " prod ", status: "archived" })).toEqual({
      archived: undefined,
      locked: undefined,
      page: 2,
      page_size: undefined,
      search: "prod",
      status: "archived",
    });

    expect(mapVaultFormToCreateDto({ description: " notes ", name: " Production " })).toEqual({
      description: "notes",
      name: "Production",
    });
  });

  it("hides an action only when backend permission explicitly denies it", () => {
    expect(canUseVaultAction({}, "update")).toBe(true);
    expect(canUseVaultAction({ update: false }, "update")).toBe(false);
  });
});
