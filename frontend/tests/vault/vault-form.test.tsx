import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { VaultForm } from "@/features/vault/components/vault-form";

describe("VaultForm", () => {
  it("submits validated vault metadata", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<VaultForm onSubmit={onSubmit} submitLabel="Create vault" />);

    await user.type(screen.getByLabelText(/name/i), "Production");
    await user.type(screen.getByLabelText(/description/i), "Non-sensitive metadata");
    await user.click(screen.getByRole("button", { name: "Create vault" }));

    expect(onSubmit).toHaveBeenCalledWith(
      {
        description: "Non-sensitive metadata",
        name: "Production",
      },
      expect.anything(),
    );
  });

  it("blocks invalid vault names", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<VaultForm onSubmit={onSubmit} submitLabel="Create vault" />);

    await user.type(screen.getByLabelText(/name/i), "ab");
    await user.click(screen.getByRole("button", { name: "Create vault" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("at least 3 characters");
    expect(onSubmit).not.toHaveBeenCalled();
  });
});
