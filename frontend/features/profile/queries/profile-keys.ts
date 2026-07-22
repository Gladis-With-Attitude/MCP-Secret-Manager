const profileQueryKeys = {
  root: () => ["profile"] as const,
  security: () => ["profile", "security"] as const,
  sessions: () => ["profile", "sessions"] as const,
  user: () => ["profile", "current"] as const,
};

export { profileQueryKeys };
