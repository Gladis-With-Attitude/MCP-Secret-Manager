export { createAuthError, createSessionExpiredError, normalizeAuthError } from "./errors";
export { canAccessRoute, isSafeRedirectPath } from "./routes";
export {
  createAuthenticatedAuthState,
  createAuthErrorState,
  createExpiredAuthState,
  createInitializingAuthState,
  createUnauthenticatedAuthState,
  isSessionExpired,
  resolveSessionState,
} from "./session";
export { defaultAuthCapabilities, defaultSessionClient, signInWithApiKey } from "./session-client";
export type {
  AuthError,
  AuthErrorKind,
  AuthExtensionCapabilities,
  AuthMethod,
  AuthSessionClient,
  AuthState,
  AuthStatus,
  CurrentUser,
  RouteAccess,
  RouteProtection,
  Session,
} from "./types";
