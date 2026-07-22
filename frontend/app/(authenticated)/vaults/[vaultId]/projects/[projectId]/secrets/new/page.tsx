import { SecretCreatePage } from "@/features/secret";

type NewSecretRoutePageProps = {
  params: Promise<{
    projectId: string;
    vaultId: string;
  }>;
};

export default async function NewSecretRoutePage({ params }: NewSecretRoutePageProps) {
  const { projectId, vaultId } = await params;

  return <SecretCreatePage projectId={projectId} vaultId={vaultId} />;
}
