import { describe, expect, it } from "vitest";

import { roleAssignmentSchema, roleFormSchema } from "@/features/rbac";

describe("RBAC validation", () => {
  it("accepts valid role metadata and permission selection", () => {
    const result = roleFormSchema.safeParse({
      description: "Security administrators",
      name: "security-admin",
      permissionIds: ["perm_1"],
    });

    expect(result.success).toBe(true);
  });

  it("rejects ambiguous role names and empty permissions", () => {
    const result = roleFormSchema.safeParse({
      description: "",
      name: "Admin Role",
      permissionIds: [],
    });

    expect(result.success).toBe(false);
  });

  it("requires actor and role identifiers for assignments", () => {
    const result = roleAssignmentSchema.safeParse({
      actorId: "user_1",
      roleId: "role_1",
    });

    expect(result.success).toBe(true);
  });
});
