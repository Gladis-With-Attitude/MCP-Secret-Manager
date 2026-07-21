import { ForbiddenPage } from "@/components/auth/forbidden-page";
import { Button } from "@/components/buttons/button";
import { ErrorState } from "@/components/feedback/error-state";
import { Container } from "@/components/layout/container";
import { Page } from "@/components/layout/page";
import { isApiError } from "@/lib/api";

type ProjectErrorViewProps = {
  error: unknown;
  onRetry?: () => void;
};

function ProjectErrorView({ error, onRetry }: ProjectErrorViewProps) {
  if (isApiError(error) && error.kind === "forbidden") {
    return <ForbiddenPage />;
  }

  const isNotFound = isApiError(error) && error.kind === "not_found";
  const title = isNotFound ? "Project not found" : "Unable to load projects";
  const description = isApiError(error) ? error.userMessage : "An unexpected error occurred.";

  return (
    <Page>
      <Container className="flex min-h-[60vh] items-center justify-center" size="md">
        <ErrorState
          action={
            onRetry ? (
              <Button onClick={onRetry} variant="outline">
                Retry
              </Button>
            ) : undefined
          }
          description={description}
          title={title}
        />
      </Container>
    </Page>
  );
}

export { ProjectErrorView };
