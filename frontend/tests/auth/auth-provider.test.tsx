import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import { useAuth } from "@/hooks/use-auth";
import { createQueryClient } from "@/lib/api/query-client";
import type { AuthSessionClient, Session } from "@/lib/auth";
import { AuthProvider } from "@/providers";

const activeSession: Session = {
  expiresAt: new Date(Date.now() + 60_000).toISOString(),
  user: {
    email: "user@example.test",
    id: "user-1",
    name: "User",
  },
};

const expiredSession: Session = {
  expiresAt: new Date(Date.now() - 60_000).toISOString(),
  user: {
    email: "expired@example.test",
    id: "user-2",
  },
};

function ProviderHarness({
  children,
  sessionClient,
}: {
  children: ReactNode;
  sessionClient?: AuthSessionClient;
}) {
  const queryClient = createQueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider sessionClient={sessionClient}>{children}</AuthProvider>
    </QueryClientProvider>
  );
}

function StateProbe() {
  const auth = useAuth();

  return (
    <div>
      <span>{auth.status}</span>
      <span>{auth.user?.email ?? "no-user"}</span>
      <button onClick={() => void auth.expireSession()} type="button">
        Expire
      </button>
      <button onClick={() => void auth.logout()} type="button">
        Logout
      </button>
    </div>
  );
}

describe("AuthProvider", () => {
  it("loads the current session from the injected session client", async () => {
    const sessionClient: AuthSessionClient = {
      getCurrentSession: vi.fn(async () => activeSession),
    };

    render(
      <ProviderHarness sessionClient={sessionClient}>
        <StateProbe />
      </ProviderHarness>,
    );

    expect(screen.getByText("initializing")).toBeInTheDocument();
    await screen.findByText("authenticated");
    expect(screen.getByText("user@example.test")).toBeInTheDocument();
  });

  it("marks an expired session as expired", async () => {
    const sessionClient: AuthSessionClient = {
      getCurrentSession: vi.fn(async () => expiredSession),
    };

    render(
      <ProviderHarness sessionClient={sessionClient}>
        <StateProbe />
      </ProviderHarness>,
    );

    await screen.findByText("expired");
  });

  it("clears session state when expiration is triggered", async () => {
    const user = userEvent.setup();

    render(
      <QueryClientProvider client={createQueryClient()}>
        <AuthProvider initialSession={activeSession} initialize={false}>
          <StateProbe />
        </AuthProvider>
      </QueryClientProvider>,
    );

    expect(screen.getByText("authenticated")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Expire" }));

    expect(screen.getByText("expired")).toBeInTheDocument();
  });

  it("calls logout and clears TanStack Query cache", async () => {
    const user = userEvent.setup();
    const queryClient = createQueryClient();
    const clearSpy = vi.spyOn(queryClient, "clear");
    const logout = vi.fn(async () => undefined);

    queryClient.setQueryData(["sensitive"], { value: "temporary" });

    render(
      <QueryClientProvider client={queryClient}>
        <AuthProvider
          initialSession={activeSession}
          initialize={false}
          sessionClient={{ getCurrentSession: vi.fn(async () => activeSession), logout }}
        >
          <StateProbe />
        </AuthProvider>
      </QueryClientProvider>,
    );

    await user.click(screen.getByRole("button", { name: "Logout" }));

    await waitFor(() => expect(logout).toHaveBeenCalledTimes(1));
    expect(clearSpy).toHaveBeenCalled();
    expect(queryClient.getQueryData(["sensitive"])).toBeUndefined();
    expect(screen.getByText("unauthenticated")).toBeInTheDocument();
  });
});
