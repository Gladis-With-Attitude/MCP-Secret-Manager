type VaultStatus = "active" | "archived" | "locked";

type VaultPermission = "archive" | "create" | "delete" | "lock" | "read" | "update";

type VaultPermissions = Partial<Record<VaultPermission, boolean>>;

type Vault = {
  archived: boolean;
  createdAt?: string | null;
  createdBy?: string | null;
  description?: string | null;
  id: string;
  locked: boolean;
  name: string;
  permissions: VaultPermissions;
  projectCount?: number | null;
  secretCount?: number | null;
  status: VaultStatus;
  updatedAt?: string | null;
};

type VaultListFilters = {
  archived?: boolean;
  locked?: boolean;
  page?: number;
  pageSize?: number;
  search?: string;
  status?: VaultStatus | "all";
};

type VaultList = {
  items: Vault[];
  pagination: {
    hasNextPage?: boolean;
    hasPreviousPage?: boolean;
    page?: number;
    pageSize?: number;
    total?: number;
  };
  permissions: VaultPermissions;
};

type VaultFormValues = {
  description?: string;
  name: string;
};

export type {
  Vault,
  VaultFormValues,
  VaultList,
  VaultListFilters,
  VaultPermission,
  VaultPermissions,
  VaultStatus,
};
