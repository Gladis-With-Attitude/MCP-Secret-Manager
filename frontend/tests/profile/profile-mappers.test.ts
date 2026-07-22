import { describe, expect, it } from "vitest";

import {
  canUseProfileAction,
  mapAccountSecurityDtoToAccountSecurity,
  mapActiveSessionListResponseToActiveSessions,
  mapChangePasswordToDto,
  mapProfileFormToUpdateDto,
  mapUserProfileDtoToUserProfile,
} from "@/features/profile";

describe("profile mappers", () => {
  it("maps current profile metadata without sensitive fields", () => {
    const profile = mapUserProfileDtoToUserProfile({
      account_type: "human",
      email: "user@example.com",
      email_editable: false,
      id: "user_1",
      name: "User",
      permissions: { update: false },
      primary_role: "admin",
    });

    expect(profile.emailEditable).toBe(false);
    expect(profile.primaryRole).toBe("admin");
    expect(canUseProfileAction(profile.permissions, "update")).toBe(false);
  });

  it("maps security and sessions", () => {
    expect(mapAccountSecurityDtoToAccountSecurity({ mfa_enabled: true }).mfaEnabled).toBe(true);
    expect(
      mapActiveSessionListResponseToActiveSessions({
        data: [{ current: true, id: "session_1" }],
      })[0]?.current,
    ).toBe(true);
  });

  it("maps forms to backend DTOs", () => {
    expect(
      mapProfileFormToUpdateDto({
        email: " user@example.com ",
        name: " User ",
        organization: "",
      }),
    ).toEqual({
      email: "user@example.com",
      name: "User",
      organization: undefined,
    });
    expect(
      mapChangePasswordToDto({
        currentPassword: "current",
        newPassword: "new-password-123",
      }),
    ).toEqual({
      current_password: "current",
      new_password: "new-password-123",
    });
  });
});
