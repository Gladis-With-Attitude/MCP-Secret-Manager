import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { Role, UserRole } from "@/features/rbac";
import { AssignRoleDialog, RemoveRoleDialog, UserRoleList } from "@/features/rbac";

const role: Role = {
  assignmentsCount: 0,
  id: "role_1",
  kind: "custom",
  name: "reader",
  permissionIds: [],
  permissions: [],
  permissionsCount: 0,
  status: "active",
  uiPermissions: {},
};

const userRole: UserRole = {
  actorId: "user_1",
  id: "user_1:role_1",
  roleId: "role_1",
  roleName: "reader",
  scopeType: "global",
  status: "active",
};

describe("RBAC assignment components", () => {
  it("submits role assignments from the dialog", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<AssignRoleDialog isOpen onOpenChange={vi.fn()} onSubmit={onSubmit} roles={[role]} />);

    await user.type(screen.getByLabelText(/actor id/i), "user_1");
    await user.click(screen.getByRole("button", { name: "Assign" }));

    expect(onSubmit).toHaveBeenCalledWith({
      actorId: "user_1",
      roleId: "role_1",
    });
  });

  it("shows conditional revoke actions and confirms revocation", async () => {
    const user = userEvent.setup();
    const onRevoke = vi.fn();
    const onConfirm = vi.fn();

    render(<UserRoleList canRevoke onRevoke={onRevoke} userRoles={[userRole]} />);

    await user.click(screen.getByRole("button", { name: "Revoke" }));

    expect(onRevoke).toHaveBeenCalledWith(userRole);

    cleanup();
    render(
      <RemoveRoleDialog isOpen onConfirm={onConfirm} onOpenChange={vi.fn()} userRole={userRole} />,
    );
    await user.click(screen.getByRole("button", { name: "Revoke assignment" }));

    expect(onConfirm).toHaveBeenCalled();
  });
});
