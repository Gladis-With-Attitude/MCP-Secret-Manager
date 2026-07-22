import { Pagination } from "@/components/navigation/pagination";

type AuditPaginationProps = {
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  limit: number;
  offset: number;
  onOffsetChange: (offset: number) => void;
};

function AuditPagination({
  hasNextPage,
  hasPreviousPage,
  limit,
  offset,
  onOffsetChange,
}: AuditPaginationProps) {
  const currentPage = Math.floor(offset / limit) + 1;

  return (
    <Pagination
      className="mt-6"
      isNextDisabled={!hasNextPage}
      isPreviousDisabled={!hasPreviousPage}
      label="Audit pagination"
      onNext={() => onOffsetChange(offset + limit)}
      onPrevious={() => onOffsetChange(Math.max(0, offset - limit))}
      pageLabel={`Page ${currentPage}`}
    />
  );
}

export { AuditPagination };
export type { AuditPaginationProps };
