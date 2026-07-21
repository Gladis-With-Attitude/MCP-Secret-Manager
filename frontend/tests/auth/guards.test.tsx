import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AuthGuard } from "@/components/auth/auth-guard";
import { GuestGuard } from "@/components/auth/guest-guard";
import type { Session } from "@/lib/auth";

import { renderWithAuth } from "./test-utils";

const session: Session = {
  expiresAt: new Date(Date.now() + 60_000).toISOString(),
  user: {
    id: "user-1",
  },
};

const adminSession: Session = {
  expiresAt: new Date(Date.now() + 60_000).toISOString(),
  user: {
    id: "admin-1",
    isAdmin: true,
  },
};

describe("AuthGuard", () => {
  it("renders protected content for authenticated sessions", () => {
    renderWithAuth(
      <AuthGuard>
        <span>Protected content</span>
      </AuthGuard>,
      { initialSession: session },
    );

    expect(screen.getByText("Protected content")).toBeInTheDocument();
  });

  it("renders UnauthorizedPage when no session exists", () => {
    renderWithAuth(
      <AuthGuard>
        <span>Protected content</span>
      </AuthGuard>,
    );

    expect(screen.getByText("Authentication required")).toBeInTheDocument();
  });

  it("renders ForbiddenPage for admin access without admin profile flag", () => {
    renderWithAuth(
      <AuthGuard access="admin">
        <span>Admin content</span>
      </AuthGuard>,
      { initialSession: session },
    );

    expect(screen.getByText("Access unavailable")).toBeInTheDocument();
  });

  it("allows generic admin route access when the profile flag is present", () => {
    renderWithAuth(
      <AuthGuard access="admin">
        <span>Admin content</span>
      </AuthGuard>,
      { initialSession: adminSession },
    );

    expect(screen.getByText("Admin content")).toBeInTheDocument();
  });
});

describe("GuestGuard", () => {
  it("renders guest content for unauthenticated state", () => {
    renderWithAuth(
      <GuestGuard>
        <span>Guest content</span>
      </GuestGuard>,
    );

    expect(screen.getByText("Guest content")).toBeInTheDocument();
  });

  it("renders authenticated fallback when a session exists", () => {
    renderWithAuth(
      <GuestGuard authenticatedFallback={<span>Already authenticated</span>}>
        <span>Guest content</span>
      </GuestGuard>,
      { initialSession: session },
    );

    expect(screen.getByText("Already authenticated")).toBeInTheDocument();
  });
});
