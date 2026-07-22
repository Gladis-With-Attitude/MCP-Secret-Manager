import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { Permission } from "@/features/rbac";
import { PermissionMatrix } from "@/features/rbac";

const permissions: Permission[] = [
  {
    action: "read",
    group: "role",
    id: "perm_1",
    name: "role.read",
    resource: "role",
    sensitivity: "standard",
  },
  {
    action: "revoke",
    group: "actor",
    id: "perm_2",
    name: "actor.role.revoke",
    resource: "actor",
    sensitivity: "critical",
  },
];

describe("PermissionMatrix", () => {
  it("groups permissions and toggles selected permissions", async () => {
    const user = userEvent.setup();
    const onToggle = vi.fn();

    render(
      <PermissionMatrix
        onPermissionToggle={onToggle}
        permissions={permissions}
        selectedPermissionIds={["perm_1"]}
      />,
    );

    expect(screen.getByLabelText("role permissions")).toBeInTheDocument();
    expect(screen.getByText("actor.role.revoke")).toBeInTheDocument();

    await user.click(screen.getByLabelText("Select actor.role.revoke"));

    expect(onToggle).toHaveBeenCalledWith("perm_2", true);
  });
});
