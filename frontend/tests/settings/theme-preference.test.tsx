import { renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { useThemePreference } from "@/features/settings";

const themeMocks = vi.hoisted(() => ({
  setTheme: vi.fn(),
}));

vi.mock("next-themes", () => ({
  useTheme: () => ({
    setTheme: themeMocks.setTheme,
    theme: "system",
  }),
}));

describe("useThemePreference", () => {
  it("synchronizes theme changes with next-themes", () => {
    const { result } = renderHook(() => useThemePreference());

    expect(result.current.themePreference).toBe("system");
    result.current.setThemePreference("dark");

    expect(themeMocks.setTheme).toHaveBeenCalledWith("dark");
  });
});
