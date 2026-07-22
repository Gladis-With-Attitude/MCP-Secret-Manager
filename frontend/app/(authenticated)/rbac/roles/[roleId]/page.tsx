import { RoleDetailPage } from "@/features/rbac";

type RbacRoleRoutePageProps = {
  params: Promise<{
    roleId: string;
  }>;
};

export default async function RbacRoleRoutePage({ params }: RbacRoleRoutePageProps) {
  const { roleId } = await params;

  return <RoleDetailPage roleId={roleId} />;
}
