import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { PublicLayout } from "@/components/app-shell/public-layout";
import { EmptyState } from "@/components/feedback/empty-state";
import { PageHeader } from "@/components/layout/page-header";

export default function Home() {
  return (
    <PublicLayout>
      <div className="grid gap-6">
        <PageHeader
          breadcrumb={<BreadcrumbBar />}
          description="Public application entry point for the administration console."
          title="MCP Secret Manager"
        />
        <EmptyState
          description="The authenticated application shell is available through the protected route structure."
          title="Application shell ready"
        />
      </div>
    </PublicLayout>
  );
}
