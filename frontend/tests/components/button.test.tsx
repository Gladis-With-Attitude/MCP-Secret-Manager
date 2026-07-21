import { createElement } from "react";

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { Button } from "@/components/buttons/button";
import { IconButton } from "@/components/buttons/icon-button";

describe("Button", () => {
  it("renders an accessible button and handles activation", async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();

    render(createElement(Button, { onClick }, "Continue"));

    await user.click(screen.getByRole("button", { name: "Continue" }));

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("disables activation while loading", async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();

    render(createElement(Button, { isLoading: true, onClick }, "Continue"));

    const button = screen.getByRole("button", { name: "Continue" });
    await user.click(button);

    expect(button).toBeDisabled();
    expect(button).toHaveAttribute("aria-busy", "true");
    expect(onClick).not.toHaveBeenCalled();
  });
});

describe("IconButton", () => {
  it("requires a visible accessible name through aria-label", () => {
    render(
      createElement(IconButton, {
        icon: createElement("span", { "aria-hidden": true }, "i"),
        label: "Refresh",
      }),
    );

    expect(screen.getByRole("button", { name: "Refresh" })).toBeInTheDocument();
  });
});
