"use client";

import { Select } from "@/components/forms/select";

import type { LanguagePreference } from "../types/settings";

type LanguageSelectorProps = {
  disabled?: boolean;
  onChange: (value: LanguagePreference) => void;
  value: LanguagePreference;
};

const languageOptions = [
  { label: "English", value: "en" },
  { label: "Français", value: "fr" },
];

function LanguageSelector({ disabled = false, onChange, value }: LanguageSelectorProps) {
  return (
    <Select
      disabled={disabled}
      id="settings-language"
      onValueChange={(value) => onChange(value as LanguagePreference)}
      options={languageOptions}
      value={value}
    />
  );
}

export { LanguageSelector };
export type { LanguageSelectorProps };
