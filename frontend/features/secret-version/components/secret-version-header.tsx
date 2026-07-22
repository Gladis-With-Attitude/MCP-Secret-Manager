import Link from "next/link";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { Button } from "@/components/buttons/button";
import { PageHeader } from "@/components/layout/page-header";

type SecretVersionHeaderProps = {
  actions?: React.ReactNode;
  description: string;
  labels: Record<string, string>;
  parentHref: string;
  title: string;
};

function SecretVersionHeader({
  actions,
  description,
  labels,
  parentHref,
  title,
}: SecretVersionHeaderProps) {
  return (
    <PageHeader
      actions={
        <div className="flex flex-wrap gap-2">
          <Button asChild variant="outline">
            <Link href={parentHref}>Back to secret</Link>
          </Button>
          {actions}
        </div>
      }
      breadcrumb={<BreadcrumbBar labels={labels} />}
      description={description}
      title={title}
    />
  );
}

export { SecretVersionHeader };
export type { SecretVersionHeaderProps };
