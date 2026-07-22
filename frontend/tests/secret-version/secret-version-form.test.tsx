import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { SecretVersionForm } from "@/features/secret-version";

describe("SecretVersionForm", () => {
  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
  });

  it("submits a new value without persisting or retaining it in the field", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(
      <SecretVersionForm onSubmit={onSubmit} secretName="API_TOKEN" submitLabel="Create version" />,
    );

    await user.type(screen.getByLabelText(/new value/i), "sensitive-value");
    await user.type(screen.getByLabelText(/rotation note/i), "scheduled rotation");
    fireEvent.change(screen.getByLabelText(/metadata/i), {
      target: { value: '{"source":"manual"}' },
    });
    await user.click(screen.getByRole("button", { name: "Create version" }));

    expect(onSubmit).toHaveBeenCalledWith({
      makeCurrent: true,
      metadata: { source: "manual" },
      note: "scheduled rotation",
      value: "sensitive-value",
    });
    expect(localStorage.getItem("sensitive-value")).toBeNull();
    expect(sessionStorage.getItem("sensitive-value")).toBeNull();
    expect(screen.getByLabelText(/new value/i)).toHaveValue("");
  });

  it("blocks invalid metadata before submission", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<SecretVersionForm onSubmit={onSubmit} submitLabel="Create version" />);

    await user.type(screen.getByLabelText(/new value/i), "sensitive-value");
    fireEvent.change(screen.getByLabelText(/metadata/i), { target: { value: "[]" } });
    await user.click(screen.getByRole("button", { name: "Create version" }));

    expect(await screen.findByRole("alert")).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });
});
