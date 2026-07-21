import { EmptyState } from "@/components/feedback/empty-state";
import { PageHeader } from "@/components/layout/page-header";
import { Section } from "@/components/layout/section";

import { BreadcrumbBar } from "./breadcrumb-bar";

type AppPlaceholderPageProps = {
  description: string;
  emptyDescription?: string;
  title: string;
};

function AppPlaceholderPage({ description, emptyDescription, title }: AppPlaceholderPageProps) {
  return (
    <div className="mx-auto grid w-full max-w-7xl gap-6">
      <PageHeader breadcrumb={<BreadcrumbBar />} description={description} title={title} />
      <Section>
        <EmptyState
          description={
            emptyDescription ?? "This workspace area is ready for future implementation."
          }
          title={title}
        />
      </Section>
    </div>
  );
}

export { AppPlaceholderPage };
export type { AppPlaceholderPageProps };
