import { get, patch, post, remove } from "@/lib/api";

import type {
  AccountSecurityDto,
  ActiveSessionListResponseDto,
  ChangePasswordDto,
  UpdateProfileDto,
  UserProfileDto,
} from "./profile-dto";

function getCurrentProfile(): Promise<UserProfileDto> {
  return get<UserProfileDto>("/v1/me/profile");
}

function updateCurrentProfile(body: UpdateProfileDto): Promise<UserProfileDto> {
  return patch<UserProfileDto, UpdateProfileDto>("/v1/me/profile", body);
}

function getAccountSecurity(): Promise<AccountSecurityDto> {
  return get<AccountSecurityDto>("/v1/me/security");
}

function listActiveSessions(): Promise<ActiveSessionListResponseDto> {
  return get<ActiveSessionListResponseDto>("/v1/me/sessions");
}

function changePassword(body: ChangePasswordDto): Promise<void> {
  return post<void, ChangePasswordDto>("/v1/me/password", body);
}

function revokeSession(sessionId: string): Promise<void> {
  return remove<void>(`/v1/me/sessions/${sessionId}`);
}

const profileService = {
  changePassword,
  getAccountSecurity,
  getCurrentProfile,
  listActiveSessions,
  revokeSession,
  updateCurrentProfile,
};

export {
  changePassword,
  getAccountSecurity,
  getCurrentProfile,
  listActiveSessions,
  profileService,
  revokeSession,
  updateCurrentProfile,
};
