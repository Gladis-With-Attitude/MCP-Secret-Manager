import { describe, expect, it } from "vitest";

import {
  canUseProjectAction,
  mapProjectDtoToProject,
  mapProjectFiltersToParams,
  mapProjectFormToCreateDto,
  mapProjectListResponseToProjectList,
} from "@/features/project/mappers/project-mappers";

describe("project mappers", () => {
  it("maps backend project metadata to UI model", () => {
    expect(
      mapProjectDtoToProject({
        created_at: "2026-07-21T08:00:00Z",
        description: "Application project",
        id: "project_1",
        name: "API",
        permissions: { archive: false, update: true },
        secret_count: 4,
        vault_id: "vault_1",
        vault_name: "Production",
      }),
    ).toEqual({
      archived: false,
      createdAt: "2026-07-21T08:00:00Z",
      createdBy: undefined,
      description: "Application project",
      id: "project_1",
      name: "API",
      permissions: {
        archive: false,
        create: undefined,
        delete: undefined,
        read: undefined,
        update: true,
      },
      secretCount: 4,
      status: "active",
      updatedAt: undefined,
      vaultId: "vault_1",
      vaultName: "Production",
      versionCount: undefined,
    });
  });

  it("maps paginated vault-scoped list envelopes", () => {
    const result = mapProjectListResponseToProjectList(
      {
        data: [{ id: "project_1", name: "API", vault_id: "vault_1" }],
        pagination: { page: 1, pageSize: 20, total: 1 },
        permissions: { create: true },
        success: true,
      },
      "vault_1",
    );

    expect(result.vaultId).toBe("vault_1");
    expect(result.items[0]?.vaultId).toBe("vault_1");
    expect(result.permissions.create).toBe(true);
  });

  it("serializes filters and trims form values", () => {
    expect(mapProjectFiltersToParams({ page: 2, search: " api ", status: "archived" })).toEqual({
      archived: undefined,
      page: 2,
      page_size: undefined,
      search: "api",
      status: "archived",
    });

    expect(mapProjectFormToCreateDto({ description: " notes ", name: " API " })).toEqual({
      description: "notes",
      name: "API",
    });
  });

  it("hides an action only when backend permission explicitly denies it", () => {
    expect(canUseProjectAction({}, "update")).toBe(true);
    expect(canUseProjectAction({ update: false }, "update")).toBe(false);
  });
});
