import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import Home from "@/app/page";
import { createQueryClient } from "@/lib/api/query-client";
import { AuthProvider } from "@/providers";

const navigationMocks = vi.hoisted(() => ({
  push: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => ({
    push: navigationMocks.push,
  }),
}));

function renderSignInPage() {
  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={createQueryClient()}>
        <AuthProvider initialize={false}>{children}</AuthProvider>
      </QueryClientProvider>
    );
  }

  return render(<Home />, { wrapper: Wrapper });
}

describe("sign-in page", () => {
  afterEach(() => {
    navigationMocks.push.mockReset();
    vi.unstubAllGlobals();
  });

  it("opens an authenticated session after validating the API key", async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn(async (request: Request) => {
      expect(request.method).toBe("POST");
      expect(request.url).toBe("http://api.example.test/v1/auth/session");
      expect(await request.json()).toEqual({ api_key: "valid-api-key" });

      return new Response(
        JSON.stringify({
          api_key_id: "71a35966-aa7e-48af-815a-77796de636af",
          auth_method: "api_key",
          expires_at: null,
          issued_at: "2026-07-21T12:00:00+00:00",
          user: {
            email: "user@example.test",
            id: "a6ef559c-b860-4028-a050-bb7bd2244916",
            name: "Ada Lovelace",
            profile_label: "user@example.test",
            type: "user",
          },
        }),
        {
          headers: { "content-type": "application/json" },
          status: 200,
        },
      );
    });
    vi.stubGlobal("fetch", fetchMock);

    renderSignInPage();

    await user.type(screen.getByLabelText("API key"), "valid-api-key");
    await user.click(screen.getByRole("button", { name: "Sign in" }));

    await waitFor(() => expect(navigationMocks.push).toHaveBeenCalledWith("/dashboard"));
    expect(localStorage.getItem("mcp_secret_manager_api_key")).toBeNull();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("does not store a token when authentication fails", async () => {
    const user = userEvent.setup();
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        return new Response(JSON.stringify({ message: "Invalid authentication credentials." }), {
          headers: { "content-type": "application/json" },
          status: 401,
        });
      }),
    );

    renderSignInPage();

    await user.type(screen.getByLabelText("API key"), "invalid-api-key");
    await user.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByText("Authentication failed.")).toBeInTheDocument();
    expect(navigationMocks.push).not.toHaveBeenCalled();
  });
});
