import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { RevokeApiKeyDialog } from "@/features/api-key";

describe("RevokeApiKeyDialog", () => {
  it("confirms revocation without displaying full key values", async () => {
    const user = userEvent.setup();
    const onConfirm = vi.fn();

    render(
      <RevokeApiKeyDialog
        apiKey={{
          grantedPermissions: [],
          id: "key_1",
          keyPrefix: "mcp",
          name: "agent",
          permissions: {},
          roles: [],
          scopes: [],
          status: "active",
        }}
        isOpen
        onConfirm={onConfirm}
        onOpenChange={vi.fn()}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Revoke API key" }));

    expect(onConfirm).toHaveBeenCalled();
    expect(screen.queryByText(/mcp_full/i)).not.toBeInTheDocument();
  });
});
