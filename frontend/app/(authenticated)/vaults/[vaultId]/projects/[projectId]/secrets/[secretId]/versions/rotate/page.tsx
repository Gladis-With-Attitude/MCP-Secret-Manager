import { SecretVersionRotatePage } from "@/features/secret-version";

type RotateSecretRoutePageProps = {
  params: Promise<{
    projectId: string;
    secretId: string;
    vaultId: string;
  }>;
};

export default async function RotateSecretRoutePage({ params }: RotateSecretRoutePageProps) {
  const { projectId, secretId, vaultId } = await params;

  return <SecretVersionRotatePage projectId={projectId} secretId={secretId} vaultId={vaultId} />;
}
