import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ApiKeyCreatedDialog } from "@/features/api-key";

describe("ApiKeyCreatedDialog", () => {
  const writeText = vi.fn();

  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    writeText.mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText },
    });
  });

  it("displays a created key once, copies it and clears state on close", async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();

    render(
      <ApiKeyCreatedDialog
        createdApiKey={{
          apiKeyValue: "mcp_full_api_key",
          metadata: {
            grantedPermissions: [],
            id: "key_1",
            name: "agent",
            permissions: {},
            roles: [],
            scopes: [],
            status: "active",
          },
        }}
        onClose={onClose}
      />,
    );

    expect(screen.getByText("mcp_full_api_key")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Copy" }));

    expect(await screen.findByRole("button", { name: "Copied" })).toBeInTheDocument();
    expect(localStorage.getItem("mcp_full_api_key")).toBeNull();
    expect(sessionStorage.getItem("mcp_full_api_key")).toBeNull();

    await user.click(screen.getByRole("button", { name: "I have saved it" }));

    expect(onClose).toHaveBeenCalled();
  });
});
