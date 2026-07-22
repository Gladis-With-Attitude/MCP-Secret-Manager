type SecretVersionStatus =
  "current" | "active" | "revoked" | "deprecated" | "destroyed" | "unknown";

type SecretVersionPermission = "create" | "read" | "readValue" | "restore" | "rotate" | "revoke";

type SecretVersionPermissions = Partial<Record<SecretVersionPermission, boolean>>;

type SecretVersionMetadata = Record<string, boolean | number | string>;

type SecretVersion = {
  algorithm?: string | null;
  createdAt?: string | null;
  createdBy?: string | null;
  cryptoSchemeVersion?: string | null;
  id: string;
  isCurrent: boolean;
  keyReference?: string | null;
  metadata: SecretVersionMetadata;
  note?: string | null;
  permissions: SecretVersionPermissions;
  secretId: string;
  status: SecretVersionStatus;
  version: number;
};

type SecretVersionListFilters = {
  currentOnly?: boolean;
  page?: number;
  pageSize?: number;
  status?: SecretVersionStatus | "all";
};

type SecretVersionList = {
  items: SecretVersion[];
  pagination: {
    hasNextPage?: boolean;
    hasPreviousPage?: boolean;
    page?: number;
    pageSize?: number;
    total?: number;
  };
  permissions: SecretVersionPermissions;
  secretId: string;
};

type SecretVersionFormValues = {
  makeCurrent: boolean;
  metadata: SecretVersionMetadata;
  note?: string;
  value: string;
};

type SecretVersionRestoreValues = {
  reason?: string;
  versionId: string;
};

export type {
  SecretVersion,
  SecretVersionFormValues,
  SecretVersionList,
  SecretVersionListFilters,
  SecretVersionMetadata,
  SecretVersionPermission,
  SecretVersionPermissions,
  SecretVersionRestoreValues,
  SecretVersionStatus,
};
