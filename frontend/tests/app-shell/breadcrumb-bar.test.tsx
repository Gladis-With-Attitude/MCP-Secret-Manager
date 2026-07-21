import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";

let pathname = "/dashboard";

vi.mock("next/navigation", () => ({
  usePathname: () => pathname,
}));

describe("BreadcrumbBar", () => {
  beforeEach(() => {
    pathname = "/dashboard";
  });

  it("renders breadcrumbs from the current route", () => {
    pathname = "/api-keys";

    render(<BreadcrumbBar />);

    expect(screen.getByRole("navigation", { name: "Breadcrumb" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Home" })).toHaveAttribute("href", "/");
    expect(screen.getByText("API Keys")).toHaveAttribute("aria-current", "page");
  });

  it("supports dynamic labels", () => {
    pathname = "/vaults/example-vault";

    render(<BreadcrumbBar labels={{ "example-vault": "Example Vault" }} />);

    expect(screen.getByText("Example Vault")).toHaveAttribute("aria-current", "page");
  });
});
