import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

import { EmptyState } from "../feedback/empty-state";
import { Skeleton } from "../feedback/skeleton";

type DataTableColumn<TData> = {
  cell: (row: TData) => ReactNode;
  className?: string;
  header: ReactNode;
  headerClassName?: string;
  key: string;
};

type DataTableProps<TData> = {
  caption?: string;
  className?: string;
  columns: DataTableColumn<TData>[];
  data: TData[];
  emptyState?: ReactNode;
  error?: ReactNode;
  getRowKey: (row: TData, index: number) => string;
  isLoading?: boolean;
  loadingRows?: number;
};

function DataTable<TData>({
  caption,
  className,
  columns,
  data,
  emptyState,
  error,
  getRowKey,
  isLoading = false,
  loadingRows = 4,
}: DataTableProps<TData>) {
  if (error) {
    return (
      <div className="rounded-md border border-border p-4" role="alert">
        {error}
      </div>
    );
  }

  if (!isLoading && data.length === 0) {
    return (
      <div className="rounded-md border border-border p-6">
        {emptyState ?? (
          <EmptyState description="There is no content to display." title="No content" />
        )}
      </div>
    );
  }

  return (
    <div className={cn("w-full overflow-x-auto rounded-md border border-border", className)}>
      <table className="w-full min-w-full caption-bottom text-left text-sm">
        {caption ? <caption className="sr-only">{caption}</caption> : null}
        <thead className="border-b border-border bg-muted/50">
          <tr>
            {columns.map((column) => (
              <th
                className={cn(
                  "h-10 whitespace-nowrap px-4 text-left align-middle font-medium text-muted-foreground",
                  column.headerClassName,
                )}
                key={column.key}
                scope="col"
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {isLoading
            ? Array.from({ length: loadingRows }).map((_, rowIndex) => (
                <tr className="border-b border-border last:border-0" key={rowIndex}>
                  {columns.map((column) => (
                    <td className="px-4 py-3" key={column.key}>
                      <Skeleton className="h-4 w-full max-w-40" />
                    </td>
                  ))}
                </tr>
              ))
            : data.map((row, index) => (
                <tr
                  className="border-b border-border last:border-0 hover:bg-muted/40"
                  key={getRowKey(row, index)}
                >
                  {columns.map((column) => (
                    <td
                      className={cn("px-4 py-3 align-middle text-foreground", column.className)}
                      key={column.key}
                    >
                      {column.cell(row)}
                    </td>
                  ))}
                </tr>
              ))}
        </tbody>
      </table>
    </div>
  );
}

export { DataTable };
export type { DataTableColumn, DataTableProps };
