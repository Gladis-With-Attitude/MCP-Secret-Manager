import { ProjectCreatePage } from "@/features/project";

type NewProjectRoutePageProps = {
  params: Promise<{
    vaultId: string;
  }>;
};

export default async function NewProjectRoutePage({ params }: NewProjectRoutePageProps) {
  const { vaultId } = await params;

  return <ProjectCreatePage vaultId={vaultId} />;
}
