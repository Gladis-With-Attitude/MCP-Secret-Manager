import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { AuditFilters } from "@/features/audit";

describe("AuditFilters", () => {
  it("applies search and advanced filters", async () => {
    const user = userEvent.setup();
    const onApply = vi.fn();

    render(
      <AuditFilters
        defaultValues={{
          action: "",
          actorId: "",
          endDate: "",
          query: "",
          resourceId: "",
          resourceType: "",
          result: "all",
          startDate: "",
        }}
        filters={{ limit: 100, offset: 50 }}
        onApply={onApply}
        onReset={vi.fn()}
      />,
    );

    await user.type(screen.getByLabelText(/search/i), "secret");
    await user.type(screen.getByLabelText(/actor/i), "actor_1");
    await user.type(screen.getByLabelText(/action/i), "secret.read");
    await user.click(screen.getByRole("button", { name: "Apply filters" }));

    expect(onApply).toHaveBeenCalledWith(
      expect.objectContaining({
        action: "secret.read",
        actorId: "actor_1",
        limit: 100,
        offset: 0,
        query: "secret",
      }),
    );
  });
});
