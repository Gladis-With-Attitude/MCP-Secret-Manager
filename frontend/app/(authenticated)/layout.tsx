import type { ReactNode } from "react";

import { DashboardLayout } from "@/components/app-shell/dashboard-layout";
import { AuthGuard } from "@/components/auth/auth-guard";

type AuthenticatedRouteLayoutProps = Readonly<{
  children: ReactNode;
}>;

export default function AuthenticatedRouteLayout({ children }: AuthenticatedRouteLayoutProps) {
  return (
    <AuthGuard>
      <DashboardLayout>{children}</DashboardLayout>
    </AuthGuard>
  );
}
