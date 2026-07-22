import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { ActiveSession } from "@/features/profile";
import { ChangePasswordDialog, RevokeSessionDialog, SessionList } from "@/features/profile";

const session: ActiveSession = {
  current: false,
  id: "session_1",
  device: "MacBook",
};

describe("profile security components", () => {
  it("submits password changes without displaying password values after close", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    const onOpenChange = vi.fn();

    render(<ChangePasswordDialog isOpen onOpenChange={onOpenChange} onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/current password/i), "old-password-123");
    await user.type(screen.getByLabelText(/new password/i), "new-password-123");
    await user.click(screen.getByRole("button", { name: "Change password" }));

    expect(onSubmit).toHaveBeenCalledWith({
      currentPassword: "old-password-123",
      newPassword: "new-password-123",
    });
  });

  it("shows revoke actions only for non-current sessions", async () => {
    const user = userEvent.setup();
    const onRevoke = vi.fn();
    const onConfirm = vi.fn();

    render(<SessionList canRevoke onRevoke={onRevoke} sessions={[session]} />);
    await user.click(screen.getByRole("button", { name: "Revoke" }));
    expect(onRevoke).toHaveBeenCalledWith(session);

    cleanup();
    render(
      <RevokeSessionDialog isOpen onConfirm={onConfirm} onOpenChange={vi.fn()} session={session} />,
    );
    await user.click(screen.getByRole("button", { name: "Revoke session" }));
    expect(onConfirm).toHaveBeenCalled();
  });
});
