import type { AuthExtensionCapabilities, AuthSessionClient } from "./types";

const defaultAuthCapabilities: AuthExtensionCapabilities = {
  mfa: false,
  oauth: false,
  oidc: false,
  passkeys: false,
  sso: false,
  webAuthn: false,
};

const defaultSessionClient: AuthSessionClient = {
  getCurrentSession: async () => null,
  logout: async () => undefined,
  refreshSession: async () => null,
};

export { defaultAuthCapabilities, defaultSessionClient };
