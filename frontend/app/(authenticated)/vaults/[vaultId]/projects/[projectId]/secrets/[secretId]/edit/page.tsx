import { SecretEditPage } from "@/features/secret";

type EditSecretRoutePageProps = {
  params: Promise<{
    projectId: string;
    secretId: string;
    vaultId: string;
  }>;
};

export default async function EditSecretRoutePage({ params }: EditSecretRoutePageProps) {
  const { projectId, secretId, vaultId } = await params;

  return <SecretEditPage projectId={projectId} secretId={secretId} vaultId={vaultId} />;
}
