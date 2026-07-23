import type { ReactNode } from "react";

type AuthStatus = "authenticated" | "error" | "expired" | "initializing" | "unauthenticated";

type AuthErrorKind = "forbidden" | "network" | "session_expired" | "unauthorized" | "unknown";

type AuthMethod = "api_key" | "cookie" | "mfa" | "oauth" | "oidc" | "passkey" | "sso" | "webauthn";

type CurrentUser = {
  avatarUrl?: string | null;
  email?: string | null;
  id: string;
  isAdmin?: boolean;
  name?: string | null;
  profileLabel?: string | null;
};

type Session = {
  authMethod?: AuthMethod;
  expiresAt?: string | null;
  issuedAt?: string | null;
  user: CurrentUser;
};

type AuthError = {
  cause?: unknown;
  code?: string;
  kind: AuthErrorKind;
  message: string;
};

type AuthState = {
  error: AuthError | null;
  session: Session | null;
  status: AuthStatus;
  user: CurrentUser | null;
};

type AuthExtensionCapabilities = {
  mfa: boolean;
  oauth: boolean;
  oidc: boolean;
  passkeys: boolean;
  sso: boolean;
  webAuthn: boolean;
};

type AuthSessionClient = {
  getCurrentSession: () => Promise<Session | null>;
  loginWithApiKey?: (apiKey: string) => Promise<Session>;
  logout?: () => Promise<void>;
  refreshSession?: () => Promise<Session | null>;
};

type RouteAccess = "admin" | "authenticated" | "public" | "rbac";

type RouteProtection = {
  access: RouteAccess;
  fallback?: ReactNode;
  redirectTo?: string;
};

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
};
