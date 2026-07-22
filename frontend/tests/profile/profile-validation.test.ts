import { describe, expect, it } from "vitest";

import { changePasswordSchema, profileFormSchema } from "@/features/profile";

describe("profile validation", () => {
  it("accepts valid non-sensitive profile fields", () => {
    const result = profileFormSchema.safeParse({
      email: "user@example.com",
      name: "Security User",
      organization: "OpenClaw",
    });

    expect(result.success).toBe(true);
  });

  it("rejects invalid emails and weak password changes", () => {
    expect(profileFormSchema.safeParse({ email: "bad", name: "A" }).success).toBe(false);
    expect(
      changePasswordSchema.safeParse({
        currentPassword: "same-password",
        newPassword: "same-password",
      }).success,
    ).toBe(false);
  });
});
