import type { ReactNode } from "react";

import { ErrorState } from "@/components/feedback/error-state";
import { Container } from "@/components/layout/container";
import { Page } from "@/components/layout/page";

type UnauthorizedPageProps = {
  action?: ReactNode;
  description?: string;
  title?: string;
};

function UnauthorizedPage({
  action,
  description = "A valid session is required to access this page.",
  title = "Authentication required",
}: UnauthorizedPageProps) {
  return (
    <Page>
      <Container className="flex min-h-[60vh] items-center justify-center" size="sm">
        <ErrorState action={action} description={description} title={title} />
      </Container>
    </Page>
  );
}

export { UnauthorizedPage };
export type { UnauthorizedPageProps };
