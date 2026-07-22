import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { NotificationSettings } from "@/features/settings";

describe("NotificationSettings", () => {
  it("submits accessible notification preferences", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(
      <NotificationSettings
        notifications={{
          auditAlerts: true,
          emailEnabled: true,
          inAppEnabled: true,
          productUpdates: false,
          securityAlerts: true,
        }}
        onSubmit={onSubmit}
      />,
    );

    await user.click(screen.getByLabelText(/product updates/i));
    await user.click(screen.getByRole("button", { name: "Save notifications" }));

    expect(onSubmit).toHaveBeenCalledWith({
      auditAlerts: true,
      emailEnabled: true,
      inAppEnabled: true,
      productUpdates: true,
      securityAlerts: true,
    });
  });
});
