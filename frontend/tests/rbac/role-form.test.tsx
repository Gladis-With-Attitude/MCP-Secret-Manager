import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { Permission } from "@/features/rbac";
import { RoleForm } from "@/features/rbac";

const permissions: Permission[] = [
  {
    action: "read",
    group: "role",
    id: "perm_1",
    name: "role.read",
    resource: "role",
    sensitivity: "standard",
  },
];

describe("RoleForm", () => {
  it("submits validated role metadata and permissions", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<RoleForm onSubmit={onSubmit} permissions={permissions} submitLabel="Create role" />);

    await user.type(screen.getByLabelText(/role name/i), "reader");
    await user.click(screen.getByLabelText("Select role.read"));
    await user.click(screen.getByRole("button", { name: "Create role" }));

    expect(onSubmit).toHaveBeenCalledWith({
      description: undefined,
      name: "reader",
      permissionIds: ["perm_1"],
    });
  });

  it("blocks invalid roles before submission", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<RoleForm onSubmit={onSubmit} permissions={permissions} submitLabel="Create role" />);

    await user.type(screen.getByLabelText(/role name/i), "Nope");
    await user.click(screen.getByRole("button", { name: "Create role" }));

    expect(await screen.findByText(/lowercase letters/i)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });
});
