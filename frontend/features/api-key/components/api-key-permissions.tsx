import { Badge } from "@/components/display/badge";
import { EmptyState } from "@/components/feedback/empty-state";
import { Stack } from "@/components/layout/stack";

type ApiKeyPermissionsProps = {
  permissions: string[];
  roles?: string[];
  scopes: string[];
};

function ApiKeyPermissions({ permissions, roles = [], scopes }: ApiKeyPermissionsProps) {
  if (!permissions.length && !roles.length && !scopes.length) {
    return (
      <EmptyState
        description="Permission details will appear when the backend returns metadata."
        title="No permission metadata"
      />
    );
  }

  return (
    <Stack gap="sm">
      {permissions.length ? (
        <div className="flex flex-wrap gap-2" aria-label="API key permissions">
          {permissions.map((permission) => (
            <Badge key={permission} variant="info">
              {permission}
            </Badge>
          ))}
        </div>
      ) : null}
      {roles.length ? (
        <div className="flex flex-wrap gap-2" aria-label="API key roles">
          {roles.map((role) => (
            <Badge key={role} variant="success">
              {role}
            </Badge>
          ))}
        </div>
      ) : null}
      {scopes.length ? (
        <div className="flex flex-wrap gap-2" aria-label="API key scopes">
          {scopes.map((scope) => (
            <Badge key={scope} variant="neutral">
              {scope}
            </Badge>
          ))}
        </div>
      ) : null}
    </Stack>
  );
}

export { ApiKeyPermissions };
export type { ApiKeyPermissionsProps };
