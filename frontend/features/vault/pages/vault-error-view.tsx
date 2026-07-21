import { ForbiddenPage } from "@/components/auth/forbidden-page";
import { Button } from "@/components/buttons/button";
import { ErrorState } from "@/components/feedback/error-state";
import { Container } from "@/components/layout/container";
import { Page } from "@/components/layout/page";
import { isApiError } from "@/lib/api";

type VaultErrorViewProps = {
  error: unknown;
  onRetry?: () => void;
};

function VaultErrorView({ error, onRetry }: VaultErrorViewProps) {
  if (isApiError(error) && error.kind === "forbidden") {
    return <ForbiddenPage />;
  }

  const isNotFound = isApiError(error) && error.kind === "not_found";
  const title = isNotFound ? "Vault not found" : "Unable to load vaults";
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

export { VaultErrorView };
