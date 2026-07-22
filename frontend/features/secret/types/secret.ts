type SecretStatus = "active" | "archived" | "deleted" | "missing_version";

type SecretType = "api_key" | "certificate" | "generic" | "password" | "token" | "other";

type SecretPermission = "archive" | "create" | "delete" | "read" | "readValue" | "update";

type SecretPermissions = Partial<Record<SecretPermission, boolean>>;

type SecretMetadata = Record<string, boolean | number | string>;

type Secret = {
  archived: boolean;
  createdAt?: string | null;
  createdBy?: string | null;
  currentVersion?: number | null;
  description?: string | null;
  id: string;
  lastVersionAt?: string | null;
  metadata: SecretMetadata;
  name: string;
  permissions: SecretPermissions;
  projectId: string;
  projectName?: string | null;
  provider?: string | null;
  status: SecretStatus;
  tags: string[];
  type: SecretType;
  updatedAt?: string | null;
  vaultId?: string | null;
  vaultName?: string | null;
  versionCount?: number | null;
};

type SecretListFilters = {
  archived?: boolean;
  page?: number;
  pageSize?: number;
  provider?: string;
  search?: string;
  status?: SecretStatus | "all";
  type?: SecretType | "all";
};

type SecretList = {
  items: Secret[];
  pagination: {
    hasNextPage?: boolean;
    hasPreviousPage?: boolean;
    page?: number;
    pageSize?: number;
    total?: number;
  };
  permissions: SecretPermissions;
  projectId: string;
};

type SecretFormValues = {
  description?: string;
  metadata: SecretMetadata;
  name: string;
  tags: string[];
  type: SecretType;
  value?: string;
};

type SecretValueResult = {
  expiresAt?: string | null;
  value: string;
};

export type {
  Secret,
  SecretFormValues,
  SecretList,
  SecretListFilters,
  SecretMetadata,
  SecretPermission,
  SecretPermissions,
  SecretStatus,
  SecretType,
  SecretValueResult,
};
