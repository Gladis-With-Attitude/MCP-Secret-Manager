import { SecretDetailsPage } from "@/features/secret";

type SecretRoutePageProps = {
  params: Promise<{
    projectId: string;
    secretId: string;
    vaultId: string;
  }>;
};

export default async function SecretRoutePage({ params }: SecretRoutePageProps) {
  const { projectId, secretId, vaultId } = await params;

  return <SecretDetailsPage projectId={projectId} secretId={secretId} vaultId={vaultId} />;
}
