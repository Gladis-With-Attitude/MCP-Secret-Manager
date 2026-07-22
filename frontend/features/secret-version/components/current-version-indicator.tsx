import { CheckCircle2 } from "lucide-react";

type CurrentVersionIndicatorProps = {
  isCurrent: boolean;
  version: number;
};

function CurrentVersionIndicator({ isCurrent, version }: CurrentVersionIndicatorProps) {
  if (!isCurrent) {
    return <span className="text-sm text-muted-foreground">Version {version}</span>;
  }

  return (
    <span className="inline-flex items-center gap-2 text-sm font-medium text-emerald-700 dark:text-emerald-300">
      <CheckCircle2 aria-hidden="true" className="size-4" />
      Current version {version}
    </span>
  );
}

export { CurrentVersionIndicator };
export type { CurrentVersionIndicatorProps };
