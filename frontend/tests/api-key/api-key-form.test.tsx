import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ApiKeyForm } from "@/features/api-key";

describe("ApiKeyForm", () => {
  it("submits validated metadata without local token persistence", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<ApiKeyForm onSubmit={onSubmit} submitLabel="Create API key" />);

    await user.type(screen.getByLabelText(/^name/i), "openclaw-agent");
    await user.type(screen.getByLabelText(/description/i), "Production agent");
    await user.type(screen.getByLabelText(/owner id/i), "service-account-id");
    await user.clear(screen.getByLabelText(/permissions/i));
    await user.type(screen.getByLabelText(/permissions/i), "secret.read,secret.version.read");
    await user.clear(screen.getByLabelText(/scopes/i));
    await user.type(screen.getByLabelText(/scopes/i), "global");
    await user.click(screen.getByRole("button", { name: "Create API key" }));

    expect(onSubmit).toHaveBeenCalledWith({
      description: "Production agent",
      expiresAt: undefined,
      name: "openclaw-agent",
      ownerId: "service-account-id",
      ownerType: "service_account",
      permissions: ["secret.read", "secret.version.read"],
      scopes: ["global"],
    });
    expect(localStorage.length).toBe(0);
    expect(sessionStorage.length).toBe(0);
  });
});
