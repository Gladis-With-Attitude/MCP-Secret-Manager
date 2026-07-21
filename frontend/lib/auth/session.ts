import { createSessionExpiredError } from "./errors";
import type { AuthError, AuthState, Session } from "./types";

function isSessionExpired(session: Session | null, now: Date = new Date()): boolean {
  if (!session?.expiresAt) {
    return false;
  }

  const expiresAt = Date.parse(session.expiresAt);

  return Number.isFinite(expiresAt) && expiresAt <= now.getTime();
}

function createInitializingAuthState(): AuthState {
  return {
    error: null,
    session: null,
    status: "initializing",
    user: null,
  };
}

function createUnauthenticatedAuthState(error: AuthError | null = null): AuthState {
  return {
    error,
    session: null,
    status: "unauthenticated",
    user: null,
  };
}

function createAuthenticatedAuthState(session: Session): AuthState {
  return {
    error: null,
    session,
    status: "authenticated",
    user: session.user,
  };
}

function createExpiredAuthState(
  session: Session | null = null,
  error = createSessionExpiredError(),
): AuthState {
  return {
    error,
    session: null,
    status: "expired",
    user: session?.user ?? null,
  };
}

function createAuthErrorState(error: AuthError): AuthState {
  return {
    error,
    session: null,
    status: "error",
    user: null,
  };
}

function resolveSessionState(session: Session | null, now: Date = new Date()): AuthState {
  if (!session) {
    return createUnauthenticatedAuthState();
  }

  if (isSessionExpired(session, now)) {
    return createExpiredAuthState(session);
  }

  return createAuthenticatedAuthState(session);
}

export {
  createAuthenticatedAuthState,
  createAuthErrorState,
  createExpiredAuthState,
  createInitializingAuthState,
  createUnauthenticatedAuthState,
  isSessionExpired,
  resolveSessionState,
};
