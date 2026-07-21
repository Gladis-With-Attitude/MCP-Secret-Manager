"use client";

import type { ReactNode } from "react";

import { AuthLoadingScreen } from "@/components/auth/auth-loading-screen";
import { useAuth } from "@/hooks/use-auth";

type GuestGuardProps = {
  authenticatedFallback?: ReactNode;
  children: ReactNode;
  loadingFallback?: ReactNode;
};

function GuestGuard({ authenticatedFallback = null, children, loadingFallback }: GuestGuardProps) {
  const auth = useAuth();

  if (auth.isLoading) {
    return loadingFallback ?? <AuthLoadingScreen />;
  }

  if (auth.isAuthenticated) {
    return authenticatedFallback;
  }

  return children;
}

export { GuestGuard };
export type { GuestGuardProps };
