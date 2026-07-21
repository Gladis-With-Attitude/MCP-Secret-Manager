import type { ReactNode } from "react";

import { AuthenticatedLayout } from "./authenticated-layout";

type DashboardLayoutProps = {
  children: ReactNode;
};

function DashboardLayout({ children }: DashboardLayoutProps) {
  return <AuthenticatedLayout>{children}</AuthenticatedLayout>;
}

export { DashboardLayout };
export type { DashboardLayoutProps };
