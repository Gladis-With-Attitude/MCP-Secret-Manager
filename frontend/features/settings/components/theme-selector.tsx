"use client";

import { Select } from "@/components/forms/select";

import { useThemePreference } from "../hooks/use-theme-preference";
import type { ThemePreference } from "../types/settings";

type ThemeSelectorProps = {
  disabled?: boolean;
  onChange?: (value: ThemePreference) => void;
  value: ThemePreference;
};

const themeOptions = [
  { label: "Light", value: "light" },
  { label: "Dark", value: "dark" },
  { label: "System", value: "system" },
];

function ThemeSelector({ disabled = false, onChange, value }: ThemeSelectorProps) {
  const { setThemePreference } = useThemePreference();

  return (
    <Select
      disabled={disabled}
      id="settings-theme"
      onValueChange={(nextValue) => {
        const theme = nextValue as ThemePreference;
        setThemePreference(theme);
        onChange?.(theme);
      }}
      options={themeOptions}
      value={value}
    />
  );
}

export { ThemeSelector };
export type { ThemeSelectorProps };
