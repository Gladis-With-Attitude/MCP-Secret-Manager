import { ProjectListPage } from "@/features/project";

type ProjectsRoutePageProps = {
  params: Promise<{
    vaultId: string;
  }>;
};

export default async function ProjectsRoutePage({ params }: ProjectsRoutePageProps) {
  const { vaultId } = await params;

  return <ProjectListPage vaultId={vaultId} />;
}
