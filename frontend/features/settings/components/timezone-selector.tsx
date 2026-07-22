"use client";

import { Select } from "@/components/forms/select";

type TimezoneSelectorProps = {
  disabled?: boolean;
  onChange: (value: string) => void;
  value: string;
};

const timezoneOptions = [
  { label: "UTC", value: "UTC" },
  { label: "Europe/Paris", value: "Europe/Paris" },
  { label: "America/New_York", value: "America/New_York" },
  { label: "America/Los_Angeles", value: "America/Los_Angeles" },
];

function TimezoneSelector({ disabled = false, onChange, value }: TimezoneSelectorProps) {
  return (
    <Select
      disabled={disabled}
      id="settings-timezone"
      onValueChange={onChange}
      options={timezoneOptions}
      value={value}
    />
  );
}

export { TimezoneSelector };
export type { TimezoneSelectorProps };
