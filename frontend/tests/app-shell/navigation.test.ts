import { describe, expect, it } from "vitest";

import { isActiveRoute, matchPathPattern } from "@/lib/navigation/active-route";
import { createBreadcrumbs } from "@/lib/navigation/breadcrumbs";

describe("app shell navigation helpers", () => {
  it("detects exact and nested active routes", () => {
    expect(isActiveRoute("/vaults", "/vaults")).toBe(true);
    expect(isActiveRoute("/vaults/details", "/vaults")).toBe(true);
    expect(isActiveRoute("/projects", "/vaults")).toBe(false);
  });

  it("supports explicit active route patterns", () => {
    expect(matchPathPattern("/vaults/vault_1/projects/project_1", "/vaults/*/projects")).toBe(true);
    expect(
      isActiveRoute("/vaults/vault_1/projects/project_1", "/projects", ["/vaults/*/projects"]),
    ).toBe(true);
  });

  it("creates breadcrumbs from static routes", () => {
    expect(createBreadcrumbs("/api-keys")).toEqual([
      { href: "/", label: "Home" },
      { href: undefined, label: "API Keys" },
    ]);
  });

  it("supports dynamic breadcrumb labels", () => {
    expect(
      createBreadcrumbs("/vaults/example-vault", { "example-vault": "Example Vault" }),
    ).toEqual([
      { href: "/", label: "Home" },
      { href: "/vaults", label: "Vaults" },
      { href: undefined, label: "Example Vault" },
    ]);
  });
});
