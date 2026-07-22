import { UserRolePage } from "@/features/rbac";

type RbacUserRoutePageProps = {
  params: Promise<{
    userId: string;
  }>;
};

export default async function RbacUserRoutePage({ params }: RbacUserRoutePageProps) {
  const { userId } = await params;

  return <UserRolePage userId={userId} />;
}
