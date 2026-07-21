"use client";

import type { AuthProviderProps } from "./auth-provider";
import { AuthProvider } from "./auth-provider";

function SessionProvider(props: AuthProviderProps) {
  return <AuthProvider {...props} />;
}

export { SessionProvider };
