import { describe, expect, it } from "vitest";

import {
  hasPermission,
  hasRole,
  mapPermissionDtoToPermission,
  mapRoleDtoToRole,
  mapRoleFiltersToParams,
  mapRoleFormToCreateDto,
  mapRoleListResponseToRoleList,
  mapUserRoleListResponseToUserRoleList,
} from "@/features/rbac";

describe("RBAC mappers", () => {
  it("maps roles with permissions and critical sensitivity", () => {
    const role = mapRoleDtoToRole({
      assignments_count: 2,
      id: "role_1",
      is_system: true,
      name: "admin",
      permissions: [
        {
          id: "perm_1",
          name: "secret.value.read",
        },
      ],
      ui_permissions: {
        update: false,
      },
    });

    expect(role.kind).toBe("system");
    expect(role.permissions[0]?.sensitivity).toBe("critical");
    expect(role.uiPermissions.update).toBe(false);
  });

  it("maps list pagination and frontend action metadata", () => {
    const list = mapRoleListResponseToRoleList(
      {
        data: [{ id: "role_1", name: "reader" }],
        limit: 20,
        offset: 0,
        permissions: { create: true },
        total: 30,
      },
      { limit: 20, offset: 0 },
    );

    expect(list.items).toHaveLength(1);
    expect(list.pagination?.hasNextPage).toBe(true);
    expect(list.permissions.create).toBe(true);
  });

  it("maps role filters and forms to backend DTOs", () => {
    expect(
      mapRoleFiltersToParams({ kind: "system", query: "admin", status: "active" }),
    ).toMatchObject({
      kind: "system",
      q: "admin",
      status: "active",
    });
    expect(
      mapRoleFormToCreateDto({
        description: "  Admins  ",
        name: " admin ",
        permissionIds: ["perm_1"],
      }),
    ).toEqual({
      description: "Admins",
      name: "admin",
      permission_ids: ["perm_1"],
    });
  });

  it("maps user assignments and helper checks", () => {
    const assignmentList = mapUserRoleListResponseToUserRoleList(
      {
        actor_id: "user_1",
        data: [{ role_id: "role_1", role_name: "admin" }],
        permissions: { revoke: true },
      },
      "fallback",
    );

    expect(assignmentList.actorId).toBe("user_1");
    expect(hasRole(assignmentList.items, "admin")).toBe(true);
    expect(
      hasPermission(
        [mapPermissionDtoToPermission({ id: "perm_1", name: "role.read" })],
        "role.read",
      ),
    ).toBe(true);
  });
});
