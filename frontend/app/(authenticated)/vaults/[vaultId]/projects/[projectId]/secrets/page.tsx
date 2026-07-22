import { SecretListPage } from "@/features/secret";

type SecretsRoutePageProps = {
  params: Promise<{
    projectId: string;
    vaultId: string;
  }>;
};

export default async function SecretsRoutePage({ params }: SecretsRoutePageProps) {
  const { projectId, vaultId } = await params;

  return <SecretListPage projectId={projectId} vaultId={vaultId} />;
}
