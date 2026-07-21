import type { ReactNode } from "react";

import { ForbiddenState } from "@/components/feedback/forbidden-state";
import { Container } from "@/components/layout/container";
import { Page } from "@/components/layout/page";

type ForbiddenPageProps = {
  action?: ReactNode;
  description?: string;
  title?: string;
};

function ForbiddenPage({
  action,
  description = "You do not have access to this page.",
  title = "Access unavailable",
}: ForbiddenPageProps) {
  return (
    <Page>
      <Container className="flex min-h-[60vh] items-center justify-center" size="sm">
        <ForbiddenState action={action} description={description} title={title} />
      </Container>
    </Page>
  );
}

export { ForbiddenPage };
export type { ForbiddenPageProps };
