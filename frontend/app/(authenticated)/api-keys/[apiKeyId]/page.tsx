import { ApiKeyDetailPage } from "@/features/api-key";

type ApiKeyRoutePageProps = {
  params: Promise<{
    apiKeyId: string;
  }>;
};

export default async function ApiKeyRoutePage({ params }: ApiKeyRoutePageProps) {
  const { apiKeyId } = await params;

  return <ApiKeyDetailPage apiKeyId={apiKeyId} />;
}
