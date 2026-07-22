import type {
  AccountSecurityDto,
  ActiveSessionDto,
  ActiveSessionListResponseDto,
  ChangePasswordDto,
  ProfilePermissionDto,
  UpdateProfileDto,
  UserProfileDto,
} from "../api/profile-dto";
import type {
  AccountSecurity,
  ActiveSession,
  ChangePasswordValues,
  ProfileFormValues,
  ProfilePermissions,
  UserProfile,
} from "../types/profile";

function mapProfilePermissions(dto?: ProfilePermissionDto | null): ProfilePermissions {
  return {
    changePassword: dto?.change_password,
    read: dto?.read,
    revokeSessions: dto?.revoke_sessions,
    update: dto?.update,
  };
}

function mapUserProfileDtoToUserProfile(dto: UserProfileDto): UserProfile {
  return {
    accountType:
      dto.account_type === "human" || dto.account_type === "service" ? dto.account_type : "unknown",
    avatarUrl: dto.avatar_url ?? undefined,
    createdAt: dto.created_at ?? undefined,
    email: dto.email ?? undefined,
    emailEditable: dto.email_editable === true,
    id: dto.id,
    lastLoginAt: dto.last_login_at ?? undefined,
    name: dto.name?.trim() || dto.email || dto.id,
    organization: dto.organization ?? undefined,
    permissions: mapProfilePermissions(dto.permissions),
    primaryRole: dto.primary_role ?? undefined,
  };
}

function mapAccountSecurityDtoToAccountSecurity(dto: AccountSecurityDto): AccountSecurity {
  return {
    mfaEnabled: dto.mfa_enabled === true,
    passkeysEnabled: dto.passkeys_enabled === true,
    passwordChangeAvailable: dto.password_change_available === true,
    recoveryKeysAvailable: dto.recovery_keys_available === true,
    webAuthnEnabled: dto.webauthn_enabled === true,
  };
}

function mapActiveSessionDtoToActiveSession(dto: ActiveSessionDto): ActiveSession {
  return {
    current: dto.current === true,
    device: dto.device ?? undefined,
    expiresAt: dto.expires_at ?? undefined,
    id: dto.id,
    ipAddress: dto.ip_address ?? undefined,
    lastSeenAt: dto.last_seen_at ?? undefined,
    location: dto.location ?? undefined,
    userAgent: dto.user_agent ?? undefined,
  };
}

function mapActiveSessionListResponseToActiveSessions(
  dto: ActiveSessionListResponseDto,
): ActiveSession[] {
  const items = Array.isArray(dto) ? dto : dto.data;

  return items.map(mapActiveSessionDtoToActiveSession);
}

function mapProfileFormToUpdateDto(values: ProfileFormValues): UpdateProfileDto {
  return {
    email: values.email?.trim() || undefined,
    name: values.name.trim(),
    organization: values.organization?.trim() || undefined,
  };
}

function mapChangePasswordToDto(values: ChangePasswordValues): ChangePasswordDto {
  return {
    current_password: values.currentPassword,
    new_password: values.newPassword,
  };
}

function canUseProfileAction(
  permissions: ProfilePermissions,
  action: keyof ProfilePermissions,
): boolean {
  return permissions[action] !== false;
}

export {
  canUseProfileAction,
  mapAccountSecurityDtoToAccountSecurity,
  mapActiveSessionDtoToActiveSession,
  mapActiveSessionListResponseToActiveSessions,
  mapChangePasswordToDto,
  mapProfileFormToUpdateDto,
  mapProfilePermissions,
  mapUserProfileDtoToUserProfile,
};
