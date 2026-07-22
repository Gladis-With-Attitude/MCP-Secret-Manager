import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import {
  settingsQueryKeys,
  useUpdateNotificationsMutation,
  useUpdatePreferencesMutation,
} from "@/features/settings";
import { createQueryClient } from "@/lib/api/query-client";

const settingsServiceMocks = vi.hoisted(() => ({
  updateNotifications: vi.fn(async () => ({
    email_enabled: false,
    in_app_enabled: true,
    security_alerts: true,
  })),
  updatePreferences: vi.fn(async () => ({
    date_time_format: "short",
    display_density: "compact",
    language: "fr",
    theme: "dark",
    timezone: "Europe/Paris",
  })),
}));

vi.mock("@/features/settings/api/settings-service", () => ({
  updateNotifications: settingsServiceMocks.updateNotifications,
  updatePreferences: settingsServiceMocks.updatePreferences,
}));

function createWrapper() {
  const queryClient = createQueryClient();

  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  }

  return { queryClient, Wrapper };
}

describe("settings mutations", () => {
  it("updates preferences and invalidates settings cache", async () => {
    const { queryClient, Wrapper } = createWrapper();
    queryClient.setQueryData(settingsQueryKeys.settings(), { preferences: {} });
    const { result } = renderHook(() => useUpdatePreferencesMutation(), { wrapper: Wrapper });

    result.current.mutate({
      dateTimeFormat: "short",
      displayDensity: "compact",
      language: "fr",
      theme: "dark",
      timezone: "Europe/Paris",
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(settingsServiceMocks.updatePreferences).toHaveBeenCalledWith({
      date_time_format: "short",
      display_density: "compact",
      language: "fr",
      theme: "dark",
      timezone: "Europe/Paris",
    });
    expect(queryClient.getQueryState(settingsQueryKeys.settings())?.isInvalidated).toBe(true);
  });

  it("updates notifications and invalidates settings cache", async () => {
    const { queryClient, Wrapper } = createWrapper();
    queryClient.setQueryData(settingsQueryKeys.settings(), { notifications: {} });
    const { result } = renderHook(() => useUpdateNotificationsMutation(), { wrapper: Wrapper });

    result.current.mutate({
      auditAlerts: true,
      emailEnabled: false,
      inAppEnabled: true,
      productUpdates: false,
      securityAlerts: true,
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(settingsServiceMocks.updateNotifications).toHaveBeenCalledWith({
      audit_alerts: true,
      email_enabled: false,
      in_app_enabled: true,
      product_updates: false,
      security_alerts: true,
    });
    expect(queryClient.getQueryState(settingsQueryKeys.settings())?.isInvalidated).toBe(true);
  });
});
