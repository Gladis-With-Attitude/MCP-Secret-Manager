import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { SecretForm } from "@/features/secret/components/secret-form";

describe("SecretForm", () => {
  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
  });

  it("submits metadata and initial value without persisting the value locally", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(
      <SecretForm includeValue onSubmit={onSubmit} projectName="API" submitLabel="Create secret" />,
    );

    await user.type(screen.getByLabelText(/^name/i), "API_TOKEN");
    await user.type(screen.getByLabelText(/description/i), "Non-sensitive metadata");
    await user.type(screen.getByLabelText(/tags/i), "production, api");
    fireEvent.change(screen.getByLabelText(/metadata/i), {
      target: { value: '{"owner":"platform"}' },
    });
    await user.type(screen.getByLabelText(/initial value/i), "sensitive-value");
    await user.click(screen.getByRole("button", { name: "Create secret" }));

    expect(onSubmit).toHaveBeenCalledWith({
      description: "Non-sensitive metadata",
      metadata: { owner: "platform" },
      name: "API_TOKEN",
      tags: ["production", "api"],
      type: "generic",
      value: "sensitive-value",
    });
    expect(localStorage.getItem("sensitive-value")).toBeNull();
    expect(sessionStorage.getItem("sensitive-value")).toBeNull();
    expect(screen.getByLabelText(/initial value/i)).toHaveValue("");
  });

  it("blocks invalid names and metadata JSON", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<SecretForm includeValue onSubmit={onSubmit} submitLabel="Create secret" />);

    await user.type(screen.getByLabelText(/^name/i), "invalid-name");
    fireEvent.change(screen.getByLabelText(/metadata/i), { target: { value: "[]" } });
    await user.type(screen.getByLabelText(/initial value/i), "secret");
    await user.click(screen.getByRole("button", { name: "Create secret" }));

    expect(await screen.findAllByRole("alert")).toHaveLength(2);
    expect(onSubmit).not.toHaveBeenCalled();
  });
});
