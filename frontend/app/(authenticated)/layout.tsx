import type { ReactNode } from "react";

import { DashboardLayout } from "@/components/app-shell/dashboard-layout";

type AuthenticatedRouteLayoutProps = Readonly<{
  children: ReactNode;
}>;

export default function AuthenticatedRouteLayout({ children }: AuthenticatedRouteLayoutProps) {
  return <DashboardLayout>{children}</DashboardLayout>;
}
