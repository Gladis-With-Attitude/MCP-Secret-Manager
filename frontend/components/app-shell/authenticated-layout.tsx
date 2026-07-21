import type { ReactNode } from "react";

import { MainLayout } from "./main-layout";

type AuthenticatedLayoutProps = {
  children: ReactNode;
};

function AuthenticatedLayout({ children }: AuthenticatedLayoutProps) {
  return <MainLayout>{children}</MainLayout>;
}

export { AuthenticatedLayout };
export type { AuthenticatedLayoutProps };
