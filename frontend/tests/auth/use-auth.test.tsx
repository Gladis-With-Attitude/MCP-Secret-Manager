import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { useAuth } from "@/hooks/use-auth";

import { renderWithAuth } from "./test-utils";

function AuthProbe() {
  const auth = useAuth();

  return <span>{auth.status}</span>;
}

describe("useAuth", () => {
  it("returns the current auth context value", () => {
    renderWithAuth(<AuthProbe />);

    expect(screen.getByText("unauthenticated")).toBeInTheDocument();
  });

  it("throws outside AuthProvider", () => {
    expect(() => render(<AuthProbe />)).toThrow("useAuth must be used within AuthProvider.");
  });
});
