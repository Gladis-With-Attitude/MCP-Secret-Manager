import { RoleEditPage } from "@/features/rbac";

type RbacRoleEditRoutePageProps = {
  params: Promise<{
    roleId: string;
  }>;
};

export default async function RbacRoleEditRoutePage({ params }: RbacRoleEditRoutePageProps) {
  const { roleId } = await params;

  return <RoleEditPage roleId={roleId} />;
}
