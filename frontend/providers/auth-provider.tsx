"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { useQueryClient } from "@tanstack/react-query";
import type { ReactNode } from "react";

import {
  type AuthError,
  type AuthExtensionCapabilities,
  type AuthSessionClient,
  type AuthState,
  createAuthErrorState,
  createExpiredAuthState,
  createInitializingAuthState,
  createUnauthenticatedAuthState,
  defaultAuthCapabilities,
  defaultSessionClient,
  normalizeAuthError,
  resolveSessionState,
  type Session,
} from "@/lib/auth";

import { AuthContext } from "./auth-context";

type AuthProviderProps = Readonly<{
  capabilities?: Partial<AuthExtensionCapabilities>;
  children: ReactNode;
  initialSession?: Session | null;
  initialize?: boolean;
  onAuthError?: (error: AuthError) => void;
  onLogout?: () => void;
  onSessionExpired?: () => void;
  sessionClient?: AuthSessionClient;
}>;

async function safeCall(callback?: () => void): Promise<void> {
  callback?.();
}

function AuthProvider({
  capabilities,
  children,
  initialSession = null,
  initialize = true,
  onAuthError,
  onLogout,
  onSessionExpired,
  sessionClient = defaultSessionClient,
}: AuthProviderProps) {
  const queryClient = useQueryClient();
  const [state, setState] = useState<AuthState>(() =>
    initialSession
      ? resolveSessionState(initialSession)
      : initialize
        ? createInitializingAuthState()
        : resolveSessionState(null),
  );
  const mergedCapabilities = useMemo(
    () => ({
      ...defaultAuthCapabilities,
      ...capabilities,
    }),
    [capabilities],
  );

  const clearSensitiveState = useCallback(async () => {
    queryClient.clear();
  }, [queryClient]);

  const setSession = useCallback(
    async (session: Session | null) => {
      const nextState = resolveSessionState(session);

      if (nextState.status !== "authenticated") {
        await clearSensitiveState();
      }

      setState(nextState);

      if (nextState.status === "expired") {
        await safeCall(onSessionExpired);
      }
    },
    [clearSensitiveState, onSessionExpired],
  );

  const clearSession = useCallback(async () => {
    await clearSensitiveState();
    setState(createUnauthenticatedAuthState());
  }, [clearSensitiveState]);

  const expireSession = useCallback(async () => {
    await clearSensitiveState();
    setState((currentState) => createExpiredAuthState(currentState.session));
    await safeCall(onSessionExpired);
  }, [clearSensitiveState, onSessionExpired]);

  const refreshSession = useCallback(async () => {
    setState((currentState) => ({
      ...currentState,
      status: currentState.status === "authenticated" ? currentState.status : "initializing",
    }));

    try {
      const refreshedSession = sessionClient.refreshSession
        ? await sessionClient.refreshSession()
        : await sessionClient.getCurrentSession();

      await setSession(refreshedSession);
    } catch (error) {
      const authError = normalizeAuthError(error);
      await clearSensitiveState();
      setState(createAuthErrorState(authError));
      onAuthError?.(authError);
    }
  }, [clearSensitiveState, onAuthError, sessionClient, setSession]);

  const loginWithApiKey = useCallback(
    async (apiKey: string) => {
      if (!sessionClient.loginWithApiKey) {
        const authError = normalizeAuthError(new Error("API key login is not configured."));
        setState(createAuthErrorState(authError));
        onAuthError?.(authError);
        return;
      }

      setState((currentState) => ({
        ...currentState,
        error: null,
        status: "initializing",
      }));

      try {
        const session = await sessionClient.loginWithApiKey(apiKey);
        await setSession(session);
      } catch (error) {
        const authError = normalizeAuthError(error);
        await clearSensitiveState();
        setState(createAuthErrorState(authError));
        onAuthError?.(authError);
        throw authError;
      }
    },
    [clearSensitiveState, onAuthError, sessionClient, setSession],
  );

  const logout = useCallback(async () => {
    let logoutError: AuthError | null = null;

    try {
      await sessionClient.logout?.();
    } catch (error) {
      logoutError = normalizeAuthError(error);
      onAuthError?.(logoutError);
    } finally {
      await clearSensitiveState();
      setState(createUnauthenticatedAuthState(logoutError));
      await safeCall(onLogout);
    }
  }, [clearSensitiveState, onAuthError, onLogout, sessionClient]);

  useEffect(() => {
    if (!initialize) {
      return;
    }

    void refreshSession();
  }, [initialize, refreshSession]);

  const value = useMemo(
    () => ({
      capabilities: mergedCapabilities,
      clearSession,
      error: state.error,
      expireSession,
      isAuthenticated: state.status === "authenticated",
      isExpired: state.status === "expired",
      isLoading: state.status === "initializing",
      loginWithApiKey,
      logout,
      refreshSession,
      session: state.session,
      sessionClient,
      setSession,
      state,
      status: state.status,
      user: state.user,
    }),
    [
      clearSession,
      expireSession,
      loginWithApiKey,
      logout,
      mergedCapabilities,
      refreshSession,
      sessionClient,
      setSession,
      state,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export { AuthProvider };
export type { AuthProviderProps };
