import type { ReactNode } from "react";

import { Container } from "@/components/layout/container";
import { Page } from "@/components/layout/page";

type PublicLayoutProps = {
  children: ReactNode;
};

function PublicLayout({ children }: PublicLayoutProps) {
  return (
    <Page>
      <Container className="py-10" size="lg">
        {children}
      </Container>
    </Page>
  );
}

export { PublicLayout };
export type { PublicLayoutProps };
