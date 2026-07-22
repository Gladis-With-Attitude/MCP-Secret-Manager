type AccountType = "human" | "service" | "unknown";

type ProfilePermissions = Partial<{
  changePassword: boolean;
  read: boolean;
  revokeSessions: boolean;
  update: boolean;
}>;

type UserProfile = {
  accountType: AccountType;
  avatarUrl?: string;
  createdAt?: string;
  email?: string;
  emailEditable: boolean;
  id: string;
  lastLoginAt?: string;
  name: string;
  organization?: string;
  permissions: ProfilePermissions;
  primaryRole?: string;
};

type AccountSecurity = {
  mfaEnabled: boolean;
  passkeysEnabled: boolean;
  passwordChangeAvailable: boolean;
  recoveryKeysAvailable: boolean;
  webAuthnEnabled: boolean;
};

type ActiveSession = {
  current: boolean;
  device?: string;
  expiresAt?: string;
  id: string;
  ipAddress?: string;
  lastSeenAt?: string;
  location?: string;
  userAgent?: string;
};

type ProfileFormValues = {
  email?: string;
  name: string;
  organization?: string;
};

type ChangePasswordValues = {
  currentPassword: string;
  newPassword: string;
};

export type {
  AccountSecurity,
  AccountType,
  ActiveSession,
  ChangePasswordValues,
  ProfileFormValues,
  ProfilePermissions,
  UserProfile,
};
