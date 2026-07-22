import { QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import { useSettingsQuery } from "@/features/settings";
import { createQueryClient } from "@/lib/api/query-client";

const settingsServiceMocks = vi.hoisted(() => ({
  getSettings: vi.fn(async () => ({
    preferences: {
      language: "fr",
      theme: "dark",
      timezone: "Europe/Paris",
    },
  })),
}));

vi.mock("@/features/settings/api/settings-service", () => ({
  getSettings: settingsServiceMocks.getSettings,
}));

function createWrapper() {
  const queryClient = createQueryClient();

  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  }

  return { Wrapper };
}

describe("settings queries", () => {
  it("loads settings through the service", async () => {
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useSettingsQuery(), { wrapper: Wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(settingsServiceMocks.getSettings).toHaveBeenCalled();
    expect(result.current.data?.preferences.language).toBe("fr");
  });
});
