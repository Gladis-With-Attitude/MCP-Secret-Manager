"use client";

import { createContext } from "react";

import type {
  AuthError,
  AuthExtensionCapabilities,
  AuthSessionClient,
  AuthState,
  CurrentUser,
  Session,
} from "@/lib/auth";

type AuthContextValue = {
  capabilities: AuthExtensionCapabilities;
  clearSession: () => Promise<void>;
  error: AuthError | null;
  expireSession: () => Promise<void>;
  isAuthenticated: boolean;
  isExpired: boolean;
  isLoading: boolean;
  loginWithApiKey: (apiKey: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
  session: Session | null;
  sessionClient: AuthSessionClient;
  setSession: (session: Session | null) => Promise<void>;
  state: AuthState;
  status: AuthState["status"];
  user: CurrentUser | null;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export { AuthContext };
export type { AuthContextValue };
