import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ProjectForm } from "@/features/project/components/project-form";

describe("ProjectForm", () => {
  it("submits validated project metadata inside the vault context", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<ProjectForm onSubmit={onSubmit} submitLabel="Create project" vaultName="Production" />);

    expect(screen.getByText("This project will belong to Production.")).toBeInTheDocument();

    await user.type(screen.getByLabelText(/name/i), "API");
    await user.type(screen.getByLabelText(/description/i), "Non-sensitive metadata");
    await user.click(screen.getByRole("button", { name: "Create project" }));

    expect(onSubmit).toHaveBeenCalledWith(
      {
        description: "Non-sensitive metadata",
        name: "API",
      },
      expect.anything(),
    );
  });

  it("blocks invalid project names", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<ProjectForm onSubmit={onSubmit} submitLabel="Create project" />);

    await user.type(screen.getByLabelText(/name/i), "ab");
    await user.click(screen.getByRole("button", { name: "Create project" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("at least 3 characters");
    expect(onSubmit).not.toHaveBeenCalled();
  });
});
