type ProfilePermissionDto = {
  change_password?: boolean;
  read?: boolean;
  revoke_sessions?: boolean;
  update?: boolean;
};

type UserProfileDto = {
  account_type?: string | null;
  avatar_url?: string | null;
  created_at?: string | null;
  email?: string | null;
  email_editable?: boolean | null;
  id: string;
  last_login_at?: string | null;
  name?: string | null;
  organization?: string | null;
  permissions?: ProfilePermissionDto | null;
  primary_role?: string | null;
};

type AccountSecurityDto = {
  mfa_enabled?: boolean | null;
  passkeys_enabled?: boolean | null;
  password_change_available?: boolean | null;
  recovery_keys_available?: boolean | null;
  webauthn_enabled?: boolean | null;
};

type ActiveSessionDto = {
  current?: boolean | null;
  device?: string | null;
  expires_at?: string | null;
  id: string;
  ip_address?: string | null;
  last_seen_at?: string | null;
  location?: string | null;
  user_agent?: string | null;
};

type ActiveSessionListResponseDto =
  | ActiveSessionDto[]
  | {
      data: ActiveSessionDto[];
      permissions?: ProfilePermissionDto | null;
    };

type UpdateProfileDto = {
  email?: string;
  name: string;
  organization?: string;
};

type ChangePasswordDto = {
  current_password: string;
  new_password: string;
};

export type {
  AccountSecurityDto,
  ActiveSessionDto,
  ActiveSessionListResponseDto,
  ChangePasswordDto,
  ProfilePermissionDto,
  UpdateProfileDto,
  UserProfileDto,
};
