import { createElement } from "react";

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Dialog } from "@/components/overlay/dialog";

describe("Dialog", () => {
  it("renders a named dialog when controlled open", () => {
    render(
      createElement(
        Dialog,
        { description: "Description", open: true, title: "Dialog title" },
        "Dialog content",
      ),
    );

    expect(screen.getByRole("dialog", { name: "Dialog title" })).toBeInTheDocument();
    expect(screen.getByText("Dialog content")).toBeInTheDocument();
  });
});
