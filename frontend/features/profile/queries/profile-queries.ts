import { useQuery } from "@tanstack/react-query";

import { getAccountSecurity, getCurrentProfile, listActiveSessions } from "../api/profile-service";
import {
  mapAccountSecurityDtoToAccountSecurity,
  mapActiveSessionListResponseToActiveSessions,
  mapUserProfileDtoToUserProfile,
} from "../mappers/profile-mappers";
import { profileQueryKeys } from "./profile-keys";

function useCurrentProfileQuery() {
  return useQuery({
    queryFn: async () => mapUserProfileDtoToUserProfile(await getCurrentProfile()),
    queryKey: profileQueryKeys.user(),
    retry: false,
  });
}

function useAccountSecurityQuery() {
  return useQuery({
    queryFn: async () => mapAccountSecurityDtoToAccountSecurity(await getAccountSecurity()),
    queryKey: profileQueryKeys.security(),
    retry: false,
  });
}

function useActiveSessionsQuery() {
  return useQuery({
    queryFn: async () => mapActiveSessionListResponseToActiveSessions(await listActiveSessions()),
    queryKey: profileQueryKeys.sessions(),
    retry: false,
  });
}

export { useAccountSecurityQuery, useActiveSessionsQuery, useCurrentProfileQuery };
