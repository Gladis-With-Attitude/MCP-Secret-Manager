import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { PermissionGuard, RoleGuard, usePermission, useRole } from "@/features/rbac";

function PermissionProbe() {
  const canRead = usePermission(["role.read"], "role.read");

  return <span>{canRead ? "allowed" : "denied"}</span>;
}

function RoleProbe() {
  const hasAdmin = useRole(["admin"], "admin");

  return <span>{hasAdmin ? "has-role" : "missing-role"}</span>;
}

describe("RBAC guards", () => {
  it("renders permission children only when permission is present", () => {
    render(
      <PermissionGuard
        fallback={<span>blocked</span>}
        permission="role.update"
        permissions={["role.read"]}
      >
        <span>editable</span>
      </PermissionGuard>,
    );

    expect(screen.getByText("blocked")).toBeInTheDocument();
    expect(screen.queryByText("editable")).not.toBeInTheDocument();
  });

  it("renders role children only when role is present", () => {
    render(
      <RoleGuard fallback={<span>blocked</span>} role="admin" roles={["admin"]}>
        <span>visible</span>
      </RoleGuard>,
    );

    expect(screen.getByText("visible")).toBeInTheDocument();
  });

  it("supports dynamic hook recalculation", () => {
    const { rerender } = render(<PermissionProbe />);

    expect(screen.getByText("allowed")).toBeInTheDocument();

    rerender(<RoleProbe />);

    expect(screen.getByText("has-role")).toBeInTheDocument();
  });
});
