"use client";

import type { ReactNode } from "react";

import { AuthLoadingScreen } from "@/components/auth/auth-loading-screen";
import { ForbiddenPage } from "@/components/auth/forbidden-page";
import { SessionExpiredDialog } from "@/components/auth/session-expired-dialog";
import { UnauthorizedPage } from "@/components/auth/unauthorized-page";
import { useAuth } from "@/hooks/use-auth";
import { type AuthState, canAccessRoute, type RouteAccess } from "@/lib/auth";

type AuthGuardProps = {
  access?: RouteAccess;
  children: ReactNode;
  expiredFallback?: ReactNode;
  forbiddenFallback?: ReactNode;
  loadingFallback?: ReactNode;
  rbacCheck?: (state: AuthState) => boolean;
  unauthorizedFallback?: ReactNode;
};

function AuthGuard({
  access = "authenticated",
  children,
  expiredFallback,
  forbiddenFallback,
  loadingFallback,
  rbacCheck,
  unauthorizedFallback,
}: AuthGuardProps) {
  const auth = useAuth();

  if (access === "public") {
    return children;
  }

  if (auth.isLoading) {
    return loadingFallback ?? <AuthLoadingScreen />;
  }

  if (auth.isExpired) {
    return expiredFallback ?? <SessionExpiredDialog onAction={auth.clearSession} open />;
  }

  if (!auth.isAuthenticated) {
    return unauthorizedFallback ?? <UnauthorizedPage />;
  }

  if (!canAccessRoute(auth.state, access, rbacCheck)) {
    return forbiddenFallback ?? <ForbiddenPage />;
  }

  return children;
}

export { AuthGuard };
export type { AuthGuardProps };
