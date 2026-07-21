import { VaultEditPage } from "@/features/vault";

type EditVaultRoutePageProps = {
  params: Promise<{
    vaultId: string;
  }>;
};

export default async function EditVaultRoutePage({ params }: EditVaultRoutePageProps) {
  const { vaultId } = await params;

  return <VaultEditPage vaultId={vaultId} />;
}
