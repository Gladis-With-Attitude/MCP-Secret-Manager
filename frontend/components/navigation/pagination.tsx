import { ChevronLeft, ChevronRight } from "lucide-react";

import { Button } from "@/components/buttons/button";
import { cn } from "@/lib/utils";

type PaginationProps = {
  className?: string;
  isNextDisabled?: boolean;
  isPreviousDisabled?: boolean;
  label?: string;
  onNext?: () => void;
  onPrevious?: () => void;
  pageLabel: string;
};

function Pagination({
  className,
  isNextDisabled,
  isPreviousDisabled,
  label = "Pagination",
  onNext,
  onPrevious,
  pageLabel,
}: PaginationProps) {
  return (
    <nav aria-label={label} className={cn("flex items-center justify-between gap-3", className)}>
      <Button disabled={isPreviousDisabled} onClick={onPrevious} size="compact" variant="outline">
        <ChevronLeft aria-hidden="true" className="size-4" />
        Previous
      </Button>
      <span aria-live="polite" className="text-sm text-muted-foreground">
        {pageLabel}
      </span>
      <Button disabled={isNextDisabled} onClick={onNext} size="compact" variant="outline">
        Next
        <ChevronRight aria-hidden="true" className="size-4" />
      </Button>
    </nav>
  );
}

export { Pagination };
export type { PaginationProps };
