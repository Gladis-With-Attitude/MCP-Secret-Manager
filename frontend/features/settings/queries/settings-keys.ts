const settingsQueryKeys = {
  root: () => ["settings"] as const,
  settings: () => ["settings", "current"] as const,
};

export { settingsQueryKeys };
