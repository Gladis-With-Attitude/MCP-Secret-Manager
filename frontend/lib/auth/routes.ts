import type { AuthState, RouteAccess } from "./types";

function isSafeRedirectPath(path: string): boolean {
  return path.startsWith("/") && !path.startsWith("//") && !path.includes("://");
}

function canAccessRoute(
  state: AuthState,
  access: RouteAccess,
  customCheck?: (state: AuthState) => boolean,
): boolean {
  if (access === "public") {
    return true;
  }

  if (state.status !== "authenticated") {
    return false;
  }

  if (access === "admin") {
    return state.user?.isAdmin === true;
  }

  if (access === "rbac") {
    return customCheck ? customCheck(state) : true;
  }

  return true;
}

export { canAccessRoute, isSafeRedirectPath };
