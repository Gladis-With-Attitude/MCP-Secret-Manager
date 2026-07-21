import { QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { MainLayout } from "@/components/app-shell/main-layout";
import { createQueryClient } from "@/lib/api/query-client";
import { AuthProvider } from "@/providers";

let pathname = "/dashboard";

vi.mock("next/navigation", () => ({
  usePathname: () => pathname,
}));

function ShellWrapper({ children }: { children: ReactNode }) {
  return (
    <QueryClientProvider client={createQueryClient()}>
      <AuthProvider initialize={false}>{children}</AuthProvider>
    </QueryClientProvider>
  );
}

describe("MainLayout", () => {
  beforeEach(() => {
    pathname = "/dashboard";
  });

  it("renders shell content and active navigation", () => {
    render(<MainLayout>Content</MainLayout>, { wrapper: ShellWrapper });

    expect(screen.getByText("Content")).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "Dashboard" })[0]).toHaveAttribute(
      "aria-current",
      "page",
    );
  });

  it("opens and closes the mobile drawer", () => {
    render(<MainLayout>Content</MainLayout>, { wrapper: ShellWrapper });

    fireEvent.click(screen.getByRole("button", { name: "Open navigation" }));

    expect(screen.getByRole("dialog")).toBeInTheDocument();

    fireEvent.keyDown(document, { key: "Escape" });

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("closes the mobile drawer when overlay is clicked", () => {
    render(<MainLayout>Content</MainLayout>, { wrapper: ShellWrapper });

    fireEvent.click(screen.getByRole("button", { name: "Open navigation" }));
    fireEvent.click(screen.getByRole("button", { name: "Close navigation" }));

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
