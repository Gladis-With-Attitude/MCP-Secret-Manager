import { ProjectEditPage } from "@/features/project";

type EditProjectRoutePageProps = {
  params: Promise<{
    projectId: string;
    vaultId: string;
  }>;
};

export default async function EditProjectRoutePage({ params }: EditProjectRoutePageProps) {
  const { projectId, vaultId } = await params;

  return <ProjectEditPage projectId={projectId} vaultId={vaultId} />;
}
