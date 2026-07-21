import { createElement } from "react";

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { DataTable, type DataTableColumn } from "@/components/data-display/data-table";

type Row = {
  id: string;
  name: string;
};

const columns: DataTableColumn<Row>[] = [
  {
    cell: (row) => row.name,
    header: "Name",
    key: "name",
  },
];

describe("DataTable", () => {
  it("renders column headers and rows", () => {
    render(
      createElement(DataTable<Row>, {
        caption: "Items",
        columns,
        data: [{ id: "1", name: "Alpha" }],
        getRowKey: (row) => row.id,
      }),
    );

    expect(screen.getByRole("table", { name: "Items" })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Name" })).toBeInTheDocument();
    expect(screen.getByRole("cell", { name: "Alpha" })).toBeInTheDocument();
  });

  it("renders a generic empty state", () => {
    render(createElement(DataTable<Row>, { columns, data: [], getRowKey: (row) => row.id }));

    expect(screen.getByText("No content")).toBeInTheDocument();
  });
});
