import { SecretVersionListPage } from "@/features/secret-version";

type SecretVersionsRoutePageProps = {
  params: Promise<{
    projectId: string;
    secretId: string;
    vaultId: string;
  }>;
};

export default async function SecretVersionsRoutePage({ params }: SecretVersionsRoutePageProps) {
  const { projectId, secretId, vaultId } = await params;

  return <SecretVersionListPage projectId={projectId} secretId={secretId} vaultId={vaultId} />;
}
