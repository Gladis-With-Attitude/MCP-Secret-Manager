import type { ReactNode } from "react";

import { AuthGuard } from "@/components/auth/auth-guard";

import { MainLayout } from "./main-layout";

type AuthenticatedLayoutProps = {
  children: ReactNode;
};

function AuthenticatedLayout({ children }: AuthenticatedLayoutProps) {
  return (
    <AuthGuard>
      <MainLayout>{children}</MainLayout>
    </AuthGuard>
  );
}

export { AuthenticatedLayout };
export type { AuthenticatedLayoutProps };
