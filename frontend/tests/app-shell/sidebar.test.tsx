import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Sidebar } from "@/components/app-shell/sidebar";

describe("Sidebar", () => {
  it("renders primary navigation items", () => {
    render(<Sidebar pathname="/dashboard" />);

    expect(screen.getByRole("link", { name: "Dashboard" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Vaults" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "API Keys" })).toBeInTheDocument();
  });

  it("marks the active route", () => {
    render(<Sidebar pathname="/vaults" />);

    expect(screen.getByRole("link", { name: "Vaults" })).toHaveAttribute("aria-current", "page");
  });

  it("marks nested vault projects as active project routes", () => {
    render(<Sidebar pathname="/vaults/vault_1/projects/project_1" />);

    expect(screen.getByRole("link", { name: "Projects" })).toHaveAttribute("aria-current", "page");
  });

  it("marks nested project secrets as active secret routes", () => {
    render(<Sidebar pathname="/vaults/vault_1/projects/project_1/secrets/secret_1" />);

    expect(screen.getByRole("link", { name: "Secrets" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("link", { name: "Projects" })).not.toHaveAttribute("aria-current");
  });

  it("keeps accessible labels when collapsed", () => {
    render(<Sidebar isCollapsed pathname="/settings" />);

    expect(screen.getByRole("link", { name: "Settings" })).toHaveAttribute("title", "Settings");
  });
});
