import { get, post, remove } from "@/lib/api";
import { isApiError } from "@/lib/api/errors";

import type { AuthExtensionCapabilities, AuthSessionClient, Session } from "./types";

const defaultAuthCapabilities: AuthExtensionCapabilities = {
  mfa: false,
  oauth: false,
  oidc: false,
  passkeys: false,
  sso: false,
  webAuthn: false,
};

type CurrentSessionResponseDto = {
  api_key_id: string;
  auth_method: "api_key";
  expires_at: string | null;
  issued_at: string;
  user: {
    email: string | null;
    id: string;
    name: string;
    profile_label: string;
    type: "service_account" | "user";
  };
};

function mapCurrentSessionResponse(response: CurrentSessionResponseDto): Session {
  return {
    authMethod: "api_key",
    expiresAt: response.expires_at,
    issuedAt: response.issued_at,
    user: {
      email: response.user.email,
      id: response.user.id,
      isAdmin: response.user.type === "user",
      name: response.user.name,
      profileLabel: response.user.profile_label,
    },
  };
}

async function getCurrentSession(): Promise<Session | null> {
  try {
    return mapCurrentSessionResponse(await get<CurrentSessionResponseDto>("/v1/auth/session"));
  } catch (error) {
    if (isApiError(error) && error.kind === "unauthorized") {
      return null;
    }

    throw error;
  }
}

async function signInWithApiKey(apiKey: string): Promise<Session> {
  const token = apiKey.trim();

  if (!token) {
    throw new Error("API key is required.");
  }

  return mapCurrentSessionResponse(
    await post<CurrentSessionResponseDto, { api_key: string }>("/v1/auth/session", {
      api_key: token,
    }),
  );
}

async function logout(): Promise<void> {
  await remove("/v1/auth/session");
}

const defaultSessionClient: AuthSessionClient = {
  getCurrentSession,
  loginWithApiKey: signInWithApiKey,
  logout,
  refreshSession: getCurrentSession,
};

export { defaultAuthCapabilities, defaultSessionClient, signInWithApiKey };
