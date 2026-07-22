import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { UserProfile } from "@/features/profile";
import { ProfileForm } from "@/features/profile";

const profile: UserProfile = {
  accountType: "human",
  email: "user@example.com",
  emailEditable: false,
  id: "user_1",
  name: "User",
  permissions: {},
};

describe("ProfileForm", () => {
  it("submits validated profile metadata and keeps IdP email read-only", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<ProfileForm onSubmit={onSubmit} profile={profile} />);

    expect(screen.getByLabelText(/email/i)).toHaveAttribute("readonly");

    await user.clear(screen.getByLabelText(/name/i));
    await user.type(screen.getByLabelText(/name/i), "Security User");
    await user.click(screen.getByRole("button", { name: "Save profile" }));

    expect(onSubmit).toHaveBeenCalledWith({
      email: "user@example.com",
      name: "Security User",
      organization: undefined,
    });
  });
});
