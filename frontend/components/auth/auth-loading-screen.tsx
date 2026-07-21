import { LoadingState } from "@/components/feedback/loading-state";
import { Container } from "@/components/layout/container";
import { Page } from "@/components/layout/page";

type AuthLoadingScreenProps = {
  description?: string;
  title?: string;
};

function AuthLoadingScreen({ description, title = "Checking session" }: AuthLoadingScreenProps) {
  return (
    <Page>
      <Container className="flex min-h-[60vh] items-center justify-center" size="sm">
        <LoadingState description={description} title={title} />
      </Container>
    </Page>
  );
}

export { AuthLoadingScreen };
export type { AuthLoadingScreenProps };
