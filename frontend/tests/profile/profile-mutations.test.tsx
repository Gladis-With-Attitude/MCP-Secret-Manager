import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import {
  profileQueryKeys,
  useChangePasswordMutation,
  useRevokeSessionMutation,
  useUpdateProfileMutation,
} from "@/features/profile";
import { createQueryClient } from "@/lib/api/query-client";

const profileServiceMocks = vi.hoisted(() => ({
  changePassword: vi.fn(async () => undefined),
  revokeSession: vi.fn(async () => undefined),
  updateCurrentProfile: vi.fn(async () => ({ id: "user_1", name: "Security User" })),
}));

vi.mock("@/features/profile/api/profile-service", () => ({
  changePassword: profileServiceMocks.changePassword,
  revokeSession: profileServiceMocks.revokeSession,
  updateCurrentProfile: profileServiceMocks.updateCurrentProfile,
}));

function createWrapper() {
  const queryClient = createQueryClient();

  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  }

  return { queryClient, Wrapper };
}

describe("profile mutations", () => {
  it("updates profile cache and invalidates current profile", async () => {
    const { queryClient, Wrapper } = createWrapper();
    queryClient.setQueryData(profileQueryKeys.user(), { id: "user_1" });
    const { result } = renderHook(() => useUpdateProfileMutation(), { wrapper: Wrapper });

    result.current.mutate({ name: "Security User" });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(profileServiceMocks.updateCurrentProfile).toHaveBeenCalledWith({
      email: undefined,
      name: "Security User",
      organization: undefined,
    });
    expect(queryClient.getQueryState(profileQueryKeys.user())?.isInvalidated).toBe(true);
  });

  it("changes passwords and revokes sessions without optimistic sensitive state", async () => {
    const { queryClient, Wrapper } = createWrapper();
    queryClient.setQueryData(profileQueryKeys.sessions(), [{ id: "session_1" }]);
    const password = renderHook(() => useChangePasswordMutation(), { wrapper: Wrapper });
    const revoke = renderHook(() => useRevokeSessionMutation(), { wrapper: Wrapper });

    password.result.current.mutate({
      currentPassword: "old-password-123",
      newPassword: "new-password-123",
    });
    await waitFor(() => expect(password.result.current.isSuccess).toBe(true));

    revoke.result.current.mutate("session_1");
    await waitFor(() => expect(revoke.result.current.isSuccess).toBe(true));

    expect(profileServiceMocks.changePassword).toHaveBeenCalledWith({
      current_password: "old-password-123",
      new_password: "new-password-123",
    });
    expect(queryClient.getQueryState(profileQueryKeys.sessions())?.isInvalidated).toBe(true);
  });
});
