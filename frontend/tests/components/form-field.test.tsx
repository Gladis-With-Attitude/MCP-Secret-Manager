import { createElement } from "react";

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { FormField, type FormFieldProps } from "@/components/forms/form-field";
import { Input } from "@/components/forms/input";

describe("FormField", () => {
  it("associates the label with the control", () => {
    render(
      createElement(
        FormField,
        {
          id: "name",
          label: "Name",
        } as FormFieldProps,
        createElement(Input, { id: "name" }),
      ),
    );

    expect(screen.getByLabelText("Name")).toBeInTheDocument();
  });

  it("renders validation errors as alerts near the field", () => {
    render(
      createElement(
        FormField,
        {
          error: "Required value",
          id: "name",
          label: "Name",
        } as FormFieldProps,
        createElement(Input, { "aria-invalid": true, id: "name" }),
      ),
    );

    expect(screen.getByRole("alert")).toHaveTextContent("Required value");
  });
});
