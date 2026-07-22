type ApiKeyStatus = "active" | "expired" | "revoked" | "unknown";

type ApiKeyOwnerType = "service_account" | "user";

type ApiKeyPermission = "create" | "read" | "revoke";

type ApiKeyPermissions = Partial<Record<ApiKeyPermission, boolean>>;

type ApiKey = {
  createdAt?: string | null;
  createdBy?: string | null;
  description?: string | null;
  expiresAt?: string | null;
  grantedPermissions: string[];
  id: string;
  keyPrefix?: string | null;
  lastUsedAt?: string | null;
  name: string;
  ownerId?: string | null;
  ownerName?: string | null;
  ownerType?: ApiKeyOwnerType | string | null;
  permissions: ApiKeyPermissions;
  revokedAt?: string | null;
  roles: string[];
  scopes: string[];
  status: ApiKeyStatus;
};

type ApiKeyCreated = {
  apiKeyValue?: string;
  metadata: ApiKey;
};

type ApiKeyListFilters = {
  page?: number;
  pageSize?: number;
  search?: string;
  status?: ApiKeyStatus | "all";
};

type ApiKeyList = {
  items: ApiKey[];
  pagination: {
    hasNextPage?: boolean;
    hasPreviousPage?: boolean;
    page?: number;
    pageSize?: number;
    total?: number;
  };
  permissions: ApiKeyPermissions;
};

type ApiKeyFormValues = {
  description?: string;
  expiresAt?: string;
  name: string;
  ownerId: string;
  ownerType: ApiKeyOwnerType;
  permissions: string[];
  scopes: string[];
};

export type {
  ApiKey,
  ApiKeyCreated,
  ApiKeyFormValues,
  ApiKeyList,
  ApiKeyListFilters,
  ApiKeyOwnerType,
  ApiKeyPermission,
  ApiKeyPermissions,
  ApiKeyStatus,
};
