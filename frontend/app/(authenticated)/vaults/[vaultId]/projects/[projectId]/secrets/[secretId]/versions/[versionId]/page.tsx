import { SecretVersionDetailPage } from "@/features/secret-version";

type SecretVersionRoutePageProps = {
  params: Promise<{
    projectId: string;
    secretId: string;
    vaultId: string;
    versionId: string;
  }>;
};

export default async function SecretVersionRoutePage({ params }: SecretVersionRoutePageProps) {
  const { projectId, secretId, vaultId, versionId } = await params;

  return (
    <SecretVersionDetailPage
      projectId={projectId}
      secretId={secretId}
      vaultId={vaultId}
      versionId={versionId}
    />
  );
}
