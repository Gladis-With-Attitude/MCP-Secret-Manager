import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { RestoreVersionDialog } from "@/features/secret-version";

describe("RestoreVersionDialog", () => {
  it("confirms a metadata-only restore action", async () => {
    const user = userEvent.setup();
    const onConfirm = vi.fn();

    render(
      <RestoreVersionDialog
        isOpen
        onConfirm={onConfirm}
        onOpenChange={vi.fn()}
        version={{
          id: "version_1",
          isCurrent: false,
          metadata: {},
          permissions: {},
          secretId: "secret_1",
          status: "active",
          version: 1,
        }}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Restore version" }));

    expect(onConfirm).toHaveBeenCalled();
    expect(screen.queryByText(/secret-value/i)).not.toBeInTheDocument();
  });
});
