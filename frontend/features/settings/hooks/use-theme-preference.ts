"use client";

import { useTheme } from "next-themes";

import type { ThemePreference } from "../types/settings";

function useThemePreference() {
  const { setTheme, theme } = useTheme();

  return {
    setThemePreference: (value: ThemePreference) => setTheme(value),
    themePreference: (theme === "dark" || theme === "light" || theme === "system"
      ? theme
      : "system") as ThemePreference,
  };
}

export { useThemePreference };
