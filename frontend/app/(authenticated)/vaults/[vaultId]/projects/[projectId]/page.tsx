import { ProjectDetailsPage } from "@/features/project";

type ProjectRoutePageProps = {
  params: Promise<{
    projectId: string;
    vaultId: string;
  }>;
};

export default async function ProjectRoutePage({ params }: ProjectRoutePageProps) {
  const { projectId, vaultId } = await params;

  return <ProjectDetailsPage projectId={projectId} vaultId={vaultId} />;
}
