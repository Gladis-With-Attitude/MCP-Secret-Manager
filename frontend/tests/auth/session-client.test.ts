import { beforeEach, describe, expect, it, vi } from "vitest";

import { get, post, remove } from "@/lib/api";
import { ApiUnauthorizedError } from "@/lib/api/errors";
import { defaultSessionClient, signInWithApiKey } from "@/lib/auth/session-client";

vi.mock("@/lib/api", () => ({
  get: vi.fn(),
  post: vi.fn(),
  remove: vi.fn(),
}));

const currentSessionResponse = {
  api_key_id: "71a35966-aa7e-48af-815a-77796de636af",
  auth_method: "api_key" as const,
  expires_at: null,
  issued_at: "2026-07-21T12:00:00+00:00",
  user: {
    email: "user@example.test",
    id: "a6ef559c-b860-4028-a050-bb7bd2244916",
    name: "Ada Lovelace",
    profile_label: "User",
    type: "user" as const,
  },
};

describe("session client", () => {
  beforeEach(() => {
    vi.mocked(get).mockReset();
    vi.mocked(post).mockReset();
    vi.mocked(remove).mockReset();
  });

  it("exchanges an API key for a cookie-backed session", async () => {
    vi.mocked(post).mockResolvedValueOnce(currentSessionResponse);

    await expect(signInWithApiKey("  valid-api-key  ")).resolves.toMatchObject({
      authMethod: "api_key",
      user: {
        email: "user@example.test",
        id: "a6ef559c-b860-4028-a050-bb7bd2244916",
        isAdmin: true,
        name: "Ada Lovelace",
      },
    });
    expect(post).toHaveBeenCalledWith("/v1/auth/session", { api_key: "valid-api-key" });
  });

  it("returns null when there is no current browser session", async () => {
    vi.mocked(get).mockRejectedValueOnce(
      new ApiUnauthorizedError({
        message: "Unauthorized",
        status: 401,
      }),
    );

    await expect(defaultSessionClient.getCurrentSession()).resolves.toBeNull();
  });

  it("revokes the current browser session", async () => {
    vi.mocked(remove).mockResolvedValueOnce(undefined);
    const logout = defaultSessionClient.logout;

    if (!logout) {
      throw new Error("Logout must be configured.");
    }

    await expect(logout()).resolves.toBeUndefined();
    expect(remove).toHaveBeenCalledWith("/v1/auth/session");
  });
});
