import { VaultDetailsPage } from "@/features/vault";

type VaultRoutePageProps = {
  params: Promise<{
    vaultId: string;
  }>;
};

export default async function VaultRoutePage({ params }: VaultRoutePageProps) {
  const { vaultId } = await params;

  return <VaultDetailsPage vaultId={vaultId} />;
}
