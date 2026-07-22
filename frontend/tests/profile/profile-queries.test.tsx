import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import {
  useAccountSecurityQuery,
  useActiveSessionsQuery,
  useCurrentProfileQuery,
} from "@/features/profile";
import { createQueryClient } from "@/lib/api/query-client";

const profileServiceMocks = vi.hoisted(() => ({
  getAccountSecurity: vi.fn(async () => ({ mfa_enabled: true })),
  getCurrentProfile: vi.fn(async () => ({ id: "user_1", name: "User" })),
  listActiveSessions: vi.fn(async () => ({ data: [{ id: "session_1" }] })),
}));

vi.mock("@/features/profile/api/profile-service", () => ({
  getAccountSecurity: profileServiceMocks.getAccountSecurity,
  getCurrentProfile: profileServiceMocks.getCurrentProfile,
  listActiveSessions: profileServiceMocks.listActiveSessions,
}));

function createWrapper() {
  const queryClient = createQueryClient();

  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  }

  return { Wrapper };
}

describe("profile queries", () => {
  it("loads profile, security and sessions through services", async () => {
    const { Wrapper } = createWrapper();
    const profile = renderHook(() => useCurrentProfileQuery(), { wrapper: Wrapper });
    const security = renderHook(() => useAccountSecurityQuery(), { wrapper: Wrapper });
    const sessions = renderHook(() => useActiveSessionsQuery(), { wrapper: Wrapper });

    await waitFor(() => expect(profile.result.current.isSuccess).toBe(true));
    await waitFor(() => expect(security.result.current.isSuccess).toBe(true));
    await waitFor(() => expect(sessions.result.current.isSuccess).toBe(true));

    expect(profile.result.current.data?.id).toBe("user_1");
    expect(security.result.current.data?.mfaEnabled).toBe(true);
    expect(sessions.result.current.data?.[0]?.id).toBe("session_1");
  });
});
